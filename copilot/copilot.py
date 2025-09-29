import streamlit as st
import yaml
import json
import re
import urllib3
import boto3
import pandas as pd
from botocore.exceptions import ClientError
from cudo_client import query_cudo_api

# --- Configuration ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BLUEPRINT_PATH = "golden_config_CMM_yaml.txt"
BEDROCK_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
BEDROCK_REGION = "us-east-1"

# --- Dynamic CIQ Parser ---
def parse_ciq_params_from_yaml(yaml_path):
    """Parses YAML and extracts {full_path: {title, description, example}} from # CIQ: comments."""
    ciq_params = {}
    with open(yaml_path, 'r') as f:
        lines = f.readlines()

    path_stack = []
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue

        ciq_match = re.search(r'#\s*CIQ:\s*(.*)$', line)
        if ciq_match:
            parts = ciq_match.group(1).strip().split('|')
            title = parts[0] if len(parts) > 0 else ""
            desc = parts[1] if len(parts) > 1 else ""
            example = parts[2] if len(parts) > 2 else ""
            key_match = re.match(r'^(\s*)([\w\.]+):', line)
            if key_match:
                key = key_match.group(2)
                full_key = ".".join(path_stack + [key])
                ciq_params[full_key] = {
                    'title': title,
                    'description': desc,
                    'example': example
                }

        indent_match = re.match(r'^(\s*)([\w\.]+):', line)
        if indent_match:
            indent = len(indent_match.group(1))
            key = indent_match.group(2)
            level = indent // 2
            path_stack = path_stack[:level]
            path_stack.append(key)

    return ciq_params

def extract_default_values(yaml_path, params):
    blueprint = load_yaml_blueprint(yaml_path)
    defaults = {}

    def get_nested_value(d, key_path):
        keys = key_path.split('.')
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return ""
        return str(d) if d is not None else ""

    for param in params:
        defaults[param] = get_nested_value(blueprint, param)
    return defaults

def resolve_parameter_with_llm(user_input: str, known_params: list) -> str:
    if not known_params:
        return None
    param_list_str = "\n".join([f"- {p}" for p in known_params])
    system_prompt = """You are a precise parameter resolver. Given a user's request like "change dnn1", 
match it to EXACTLY ONE full parameter path below. Return ONLY the full path or "unknown"."""
    user_msg = f'User said: "{user_input}"\nAvailable parameters:\n{param_list_str}'
    
    client = get_bedrock_client()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 80,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_msg}],
        "temperature": 0.0
    })
    try:
        resp = client.invoke_model(body=body, modelId=BEDROCK_MODEL)
        result = json.loads(resp['body'].read())['content'][0]['text'].strip()
        return result if result in known_params else None
    except:
        return None

# --- AWS Bedrock & Helpers ---
@st.cache_resource
def get_bedrock_client():
    try:
        return boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
    except Exception as e:
        st.error(f"Error configuring AWS Bedrock: {e}.")
        st.stop()

def bedrock_invoke(system_prompt: str, user_msg: str, max_tokens: int = 512) -> str:
    client = get_bedrock_client()
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_msg}],
        "temperature": 0.1
    })
    try:
        resp = client.invoke_model(body=body, modelId=BEDROCK_MODEL)
        return json.loads(resp['body'].read())['content'][0]['text']
    except ClientError as e:
        st.error(f"Bedrock API error: {e}")
        return "Error: Unable to get response."

@st.cache_data
def load_yaml_blueprint(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error(f"Blueprint file '{path}' not found.")
        return None

@st.cache_data
def query_cudo_with_spinner(query: str, current_param: str = None) -> str:
    contextual_query = query
    if current_param:
        info = PARAM_METADATA.get(current_param, {})
        desc = info.get('description', "")
        contextual_query = f"Context: Configuring '{current_param}' which is: {desc}\nUser Question: {query}"
    with st.spinner("Searching CuDo documentation..."):
        return query_cudo_api(contextual_query)

def supervisor_classify(user_input: str, current_param: str, collected_params: list) -> str:
    all_params_str = ", ".join(collected_params)
    system_prompt = f"""Classify into ONE: 'param_answer', 'use_default', 'skip_for_now', 'change_param', 'tech_query', 'general_silly'. Return ONLY category."""
    user_msg = f"Current: '{current_param}'\nAnswered: [{all_params_str}]\nUser: \"{user_input}\""
    return bedrock_invoke(system_prompt, user_msg, 20).strip().lower()

def generate_question(param: str) -> str:
    info = PARAM_METADATA.get(param, {})
    title = info.get('title', param.split('.')[-1].replace('_', ' ').title())
    desc = info.get('description', '')
    example = info.get('example', '')
    example_text = f"\n📌 *Example:* `{example}`" if example else ""
    return f"**{title}**\n{desc}{example_text}"

def merge_yaml_with_llm(blueprint_str: str, user_values_str: str) -> str:
    try:
        blueprint_dict = yaml.safe_load(blueprint_str)
        user_values_dict = yaml.safe_load(user_values_str)
        def deep_update(base, update):
            for k, v in update.items():
                if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                    deep_update(base[k], v)
                else:
                    base[k] = v
        deep_update(blueprint_dict, user_values_dict)
        return yaml.dump(blueprint_dict, default_flow_style=False, sort_keys=False, indent=2)
    except Exception as e:
        st.warning(f"Direct merge failed ({e}), using AI...")
        system_prompt = "Merge user values into blueprint YAML. Return ONLY final YAML in a code block."
        user_msg = f"Blueprint:\n```yaml\n{blueprint_str}\n```\nUser values:\n```yaml\n{user_values_str}\n```"
        response = bedrock_invoke(system_prompt, user_msg, 4096)
        match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
        return match.group(1) if match else response

# --- Load Dynamic Schema ---
CIQ_SCHEMA = parse_ciq_params_from_yaml(BLUEPRINT_PATH)
USER_PARAMS = sorted(CIQ_SCHEMA.keys())
PARAM_METADATA = CIQ_SCHEMA
PARAM_DESCRIPTIONS = {k: v['description'] for k, v in CIQ_SCHEMA.items()}

# --- Streamlit App ---
st.set_page_config(page_title="CMM Deployment Assistant", layout="wide")
st.title("🤖 CMM Deployment Assistant")

# Elegant UI Styling
st.markdown("""
<style>
/* Modern Chat Bubbles */
.stChatMessage {
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    border-radius: 12px;
    max-width: 85%;
}
.stChatMessage[data-testid="chat-message-user"] {
    background-color: #f0f8ff;
    margin-left: auto;
    border-top-right-radius: 4px;
}
.stChatMessage[data-testid="chat-message-assistant"] {
    background-color: #f8fff8;
    margin-right: auto;
    border-top-left-radius: 4px;
}
.stChatMessage:has(div[data-testid="chat-avatar-assistant"]) div[data-testid="stMarkdownContainer"] p {
    color: #1e5631;
    font-size: 1.05em;
    line-height: 1.5;
}
.stChatMessage:has(div[data-testid="chat-avatar-user"]) div[data-testid="stMarkdownContainer"] p {
    color: #2c3e50;
}
.stProgress > div > div > div {
    background-color: #4CAF50;
    height: 12px;
    border-radius: 6px;
}
.stDownloadButton > button {
    background-color: #2E8B57;
    color: white;
    border: none;
    padding: 0.4rem 1rem;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state — ORDER IS CRITICAL
if 'history' not in st.session_state:
    st.session_state.history = []
if 'collected_values' not in st.session_state:
    st.session_state.collected_values = {}
if 'missing_params' not in st.session_state:
    st.session_state.missing_params = set(USER_PARAMS)
if 'current_param' not in st.session_state:
    st.session_state.current_param = USER_PARAMS[0] if USER_PARAMS else None
if 'final_yaml' not in st.session_state:
    st.session_state.final_yaml = ""
if 'yaml_generated' not in st.session_state:
    st.session_state.yaml_generated = False
if 'default_values' not in st.session_state:
    st.session_state.default_values = extract_default_values(BLUEPRINT_PATH, USER_PARAMS)

# Initial message + first question
if 'initial_message' not in st.session_state:
    intro = """👋 Hi! I'm your **CMM Deployment Co-Pilot**!

I’ll guide you through customizing your deployment YAML by collecting key parameters like environment name, container images, network settings, and SUPI ranges.

✨ **You can**:
- Answer directly  
- Say **“use default”** to keep the example value  
- Say **“skip”** and return later  
- Say **“change env name”** to edit any parameter — even after completion!

Let’s begin! 🚀"""
    st.session_state.history.append({"role": "assistant", "content": intro})
    if USER_PARAMS:
        first_q = generate_question(USER_PARAMS[0])
        st.session_state.history.append({"role": "assistant", "content": first_q})
        st.session_state.current_param = USER_PARAMS[0]
    st.session_state.initial_message = True

# Layout
col1, col2 = st.columns([1, 1])

# Left: Progress & YAML
with col1:
    st.header("Configuration Progress")
    total = len(USER_PARAMS)
    filled = total - len(st.session_state.missing_params)
    st.progress(filled / total if total else 0, text=f"{filled} / {total} filled")
    
    st.subheader("Parameters")
    table_data = []
    for param in USER_PARAMS:
        value = st.session_state.collected_values.get(param, "Pending...")
        status = "✅" if param in st.session_state.collected_values else "📝"
        short = param.replace("global.provisioning.", "").replace("global.containers.", "").replace("global.", "")
        table_data.append({"Status": status, "Parameter": short, "Value": value})
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.session_state.final_yaml:
        st.subheader("✅ Deployment Ready")
        st.download_button("Download YAML", st.session_state.final_yaml, "deployment_config.yaml", "text/yaml")
        st.code(st.session_state.final_yaml[:300] + "...", language='yaml')

# Right: Chat
with col2:
    st.header("Chat with your Assistant")
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if user_input := st.chat_input("Your response..."):
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                intent = supervisor_classify(
                    user_input,
                    st.session_state.current_param,
                    list(st.session_state.collected_values.keys())
                )
                response_text = ""
                
                if intent == 'param_answer':
                    st.session_state.collected_values[st.session_state.current_param] = user_input
                    st.session_state.missing_params.discard(st.session_state.current_param)
                    response_text = "✅ Got it! "
                    if st.session_state.missing_params:
                        next_p = sorted(st.session_state.missing_params)[0]
                        st.session_state.current_param = next_p
                        response_text += generate_question(next_p)
                    else:
                        st.session_state.current_param = None
                        response_text += "All done! 🎉 Your YAML is ready above."

                elif intent == 'use_default':
                    default_val = st.session_state.default_values.get(st.session_state.current_param, "N/A")
                    st.session_state.collected_values[st.session_state.current_param] = default_val
                    st.session_state.missing_params.discard(st.session_state.current_param)
                    response_text = f"✅ Using default: **{default_val}**\n"
                    if st.session_state.missing_params:
                        next_p = sorted(st.session_state.missing_params)[0]
                        st.session_state.current_param = next_p
                        response_text += generate_question(next_p)
                    else:
                        st.session_state.current_param = None
                        response_text += "All done! 🎉 Your YAML is ready above."

                elif intent == 'skip_for_now':
                    response_text = "⏸️ No problem! I'll come back to this later.\n"
                    remaining = sorted(st.session_state.missing_params)
                    if len(remaining) > 1:
                        idx = remaining.index(st.session_state.current_param)
                        st.session_state.current_param = remaining[(idx + 1) % len(remaining)]
                        response_text += generate_question(st.session_state.current_param)
                    else:
                        response_text += "This is the last one—let’s try to fill it together!"

                elif intent == 'change_param':
                    resolved = resolve_parameter_with_llm(
                        user_input,
                        list(st.session_state.collected_values.keys())
                    )
                    if resolved:
                        st.session_state.missing_params.add(resolved)
                        st.session_state.current_param = resolved
                        old_val = st.session_state.collected_values.get(resolved, "N/A")
                        base_name = resolved.split('.')[-1].replace('_', ' ')
                        response_text = f"🔄 Let's update **{base_name}** (was: `{old_val}`).\n"
                        response_text += generate_question(resolved)
                    else:
                        response_text = "I couldn't find that parameter. Try: “change env name”, “update dnn1”, or “edit NRF endpoint”."

                elif intent == 'tech_query':
                    cudo_resp = query_cudo_with_spinner(user_input, st.session_state.current_param)
                    response_text = f"📘 **Help**: {cudo_resp}\n\nBack to config: {generate_question(st.session_state.current_param)}"

                else:  # general_silly
                    response_text = bedrock_invoke(
                        "Respond warmly to off-topic chat, then gently steer back to configuration.",
                        f"User said: {user_input}",
                        120
                    )
            st.markdown(response_text)
            st.session_state.history.append({"role": "assistant", "content": response_text})
            st.rerun()

# Generate YAML once (but keep chat active)
if not st.session_state.missing_params and not st.session_state.yaml_generated:
    with st.spinner("Generating final YAML..."):
        blueprint_dict = load_yaml_blueprint(BLUEPRINT_PATH)
        if blueprint_dict:
            blueprint_str = yaml.dump(blueprint_dict, sort_keys=False)
            user_values_str = yaml.dump(st.session_state.collected_values, sort_keys=False)
            st.session_state.final_yaml = merge_yaml_with_llm(blueprint_str, user_values_str)
            st.session_state.yaml_generated = True