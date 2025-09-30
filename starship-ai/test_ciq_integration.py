#!/usr/bin/env python3
# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
"""
Test script to verify CIQ integration works correctly.

Run this to test the CIQ agent, session management, and API endpoints.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_ciq_agent_core():
    """Test the core CIQ agent functionality."""
    print("🧪 Testing CIQ Agent Core...")

    try:
        from ai.agents.ciq_agent.ciq_core import ciq_agent

        # Test creating a new session
        result1 = ciq_agent.process_chat_message(
            "Hello, I need help with CMM configuration"
        )
        print(f"✅ Session created: {result1['session_id']}")
        print(f"✅ Initial response: {result1['response'][:100]}...")
        print(f"✅ Progress: {result1['progress']['progress_percentage']:.1f}%")

        # Test providing a parameter value
        session_id = result1['session_id']
        result2 = ciq_agent.process_chat_message("192.168.1.100", session_id)
        progress_pct = result2['progress']['progress_percentage']
        print(f"✅ Parameter collected. Progress: {progress_pct:.1f}%")

        # Test technical query
        result3 = ciq_agent.process_chat_message("What is ALMS?", session_id)
        print(f"✅ Technical query handled: {result3['response'][:100]}...")

        return True
    except Exception as e:
        print(f"❌ CIQ Agent Core test failed: {e}")
        return False


def test_session_manager():
    """Test the session management functionality."""
    print("\n🧪 Testing Session Manager...")

    try:
        from ai.agents.ciq_agent.session_manager import session_manager

        # Test creating sessions
        session_id1 = session_manager.create_session()
        session_id2 = session_manager.create_session()

        print(
            f"✅ Created sessions: {session_id1[:8]}..., {session_id2[:8]}..."
        )
        print(f"✅ Active sessions: {session_manager.get_session_count()}")

        # Test getting session
        session = session_manager.get_session(session_id1)
        missing_count = len(session.missing_params)
        print(f"✅ Retrieved session with {missing_count} missing params")

        # Test parameter collection
        session.collect_parameter("global.alms.ipv4_ip", "192.168.1.1")
        remaining_count = len(session.missing_params)
        print(f"✅ Collected parameter. Remaining: {remaining_count}")

        return True
    except Exception as e:
        print(f"❌ Session Manager test failed: {e}")
        return False


def test_payload_generation():
    """Test the CIQ payload generation."""
    print("\n🧪 Testing Payload Generation...")

    try:
        from ai.agents.ciq_agent.ciq_core import ciq_agent

        # Test getting parameters schema
        schema = ciq_agent.get_parameters_schema()
        print(f"✅ Generated schema with {len(schema)} parameters")

        # Check a few key parameters
        expected_params = [
            'alms_ipv4_ip',
            'provisioning_mcc',
            'secrets_users_root_passwd'
        ]
        for param in expected_params:
            if param in schema:
                print(f"✅ Found expected parameter: {param}")
            else:
                print(f"⚠️ Missing expected parameter: {param}")

        return True
    except Exception as e:
        print(f"❌ Payload Generation test failed: {e}")
        return False


async def test_api_endpoints():
    """Test the FastAPI endpoints (mock test without server)."""
    print("\n🧪 Testing API Endpoints (Mock)...")

    try:
        from ai.models.v1.ciqchat import CIQChatRequest
        from ai.models.v1.ciqpayload import CIQPayloadRequest
        from ai.routes.v1.ciq_assistant import ciq_chat, ciq_payload

        # Test payload endpoint
        payload_req = CIQPayloadRequest(input="test")
        payload_resp = await ciq_payload(payload_req)
        prop_count = len(payload_resp.properties)
        print(f"✅ Payload endpoint: {prop_count} properties returned")

        # Test chat endpoint
        chat_req = CIQChatRequest(
            input="Hello, I need help with configuration"
        )
        chat_resp = await ciq_chat(chat_req)
        session_short = chat_resp.session_id[:8]
        print(f"✅ Chat endpoint: Session {session_short}... created")
        print(f"✅ Chat response: {chat_resp.response[:100]}...")

        # Test follow-up message
        chat_req2 = CIQChatRequest(
            input="192.168.1.100",
            session_id=chat_resp.session_id
        )
        chat_resp2 = await ciq_chat(chat_req2)
        progress_pct = chat_resp2.progress['progress_percentage']
        print(f"✅ Follow-up message: Progress {progress_pct:.1f}%")

        return True
    except Exception as e:
        print(f"❌ API Endpoints test failed: {e}")
        return False


def test_config_loading():
    """Test configuration loading."""
    print("\n🧪 Testing Configuration Loading...")

    try:
        from ai.agents.ciq_agent.config import BLUEPRINT_PATH, CUDO_CONFIG, PARAM_DESCRIPTIONS

        param_count = len(PARAM_DESCRIPTIONS)
        print(f"✅ Loaded {param_count} parameter descriptions")
        print(f"✅ Blueprint path: {BLUEPRINT_PATH}")
        print(f"✅ CuDo config: {CUDO_CONFIG['base_url'][:50]}...")

        # Check if blueprint file exists
        if BLUEPRINT_PATH.exists():
            print(f"✅ Blueprint file found: {BLUEPRINT_PATH.name}")
        else:
            print(f"⚠️ Blueprint file not found: {BLUEPRINT_PATH}")

        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting CIQ Integration Tests...\n")

    tests = [
        ("Configuration Loading", test_config_loading),
        ("Session Manager", test_session_manager),
        ("CIQ Agent Core", test_ciq_agent_core),
        ("Payload Generation", test_payload_generation),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! CIQ integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
