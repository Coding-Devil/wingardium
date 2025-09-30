#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
import logging

from fastapi import APIRouter, HTTPException, status

from ai.agents.ciq_agent.ciq_core import ciq_agent
from ai.models.v1.ciqchat import CIQChatRequest, CIQChatResponse
from ai.models.v1.ciqpayload import CIQPayloadRequest, CIQPayloadResponse
from ai.models.v1.common import FieldSchema
from ai.routes.v1.common import COMMON_ERRORS, TimedRoute

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(route_class=TimedRoute)

# common tags
tags = ['CIQ Assistant']

tag_metadata = {
    'name': 'CIQ Assistant',
    'description': 'AI CIQ Assistant APIs.'
}


@router.post(
    "/ciq/payload",
    tags=tags,
    operation_id="PostCIQPayload",
    summary="Generate CIQ payload schema",
    description="Returns CIQ schema properties for CMM deployment configuration.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': CIQPayloadResponse,
            'description': 'CIQ payload schema returned'
        }
    },
)
async def ciq_payload(req: CIQPayloadRequest) -> CIQPayloadResponse:
    """Generate CIQ payload schema with all required parameters."""
    try:
        logger.info(
            f"Generating CIQ payload schema for input: {req.input[:50]}..."
        )

        # Get parameters schema from CIQ agent
        properties_schema = ciq_agent.get_parameters_schema()

        # Convert to FieldSchema objects
        properties_obj = {}

        for field_name, schema_info in properties_schema.items():
            properties_obj[field_name] = FieldSchema(
                type=schema_info["type"],
                x_displayName=schema_info["x-displayName"],
                x_order=schema_info["x-order"]
            )

        logger.info(f"Generated schema with {len(properties_obj)} parameters")

        return CIQPayloadResponse(
            properties=properties_obj,
            response=(
                f"CIQ schema with {len(properties_obj)} parameters "
                f"returned successfully"
            )
        )
    except Exception as e:
        logger.error(f"Error generating CIQ payload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CIQ payload: {str(e)}"
        )


@router.post(
    "/ciq/chat",
    tags=tags,
    operation_id="PostCIQChat",
    summary="CIQ chat endpoint",
    description="Interactive chat for CMM deployment parameter collection with AI assistance.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': CIQChatResponse,
            'description': 'CIQ chat response with session state and progress'
        }
    },
)
async def ciq_chat(req: CIQChatRequest) -> CIQChatResponse:
    """Process chat message and manage CIQ parameter collection session."""
    try:
        logger.info(
            f"Processing CIQ chat message: {req.input[:50]}... "
            f"(session: {req.session_id})"
        )

        # Process message through CIQ agent
        result = ciq_agent.process_chat_message(req.input, req.session_id)

        progress_pct = result['progress']['progress_percentage']
        logger.info(
            f"CIQ chat processed successfully. "
            f"Session: {result['session_id']}, Progress: {progress_pct:.1f}%"
        )

        return CIQChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            progress=result["progress"],
            is_complete=result["is_complete"],
            final_yaml=result["final_yaml"]
        )
    except Exception as e:
        logger.error(f"Error in CIQ chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CIQ chat error: {str(e)}")


@router.get(
    "/ciq/session/{session_id}/progress",
    tags=tags,
    operation_id="GetCIQSessionProgress",
    summary="Get CIQ session progress",
    description="Retrieve current progress and state of a CIQ parameter collection session.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': dict,
            'description': 'CIQ session progress information'
        }
    },
)
async def get_ciq_session_progress(session_id: str) -> dict:
    """Get progress information for a CIQ session."""
    try:
        logger.info(f"Getting progress for CIQ session: {session_id}")

        progress = ciq_agent.get_session_progress(session_id)

        if progress is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )

        progress_pct = progress['progress_percentage']
        logger.info(
            f"Session progress retrieved: {progress_pct:.1f}% complete"
        )

        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session progress: {str(e)}"
        )


@router.post(
    "/ciq/session/{session_id}/yaml",
    tags=tags,
    operation_id="GenerateCIQYAML",
    summary="Generate YAML for CIQ session",
    description="Generate final deployment YAML from collected parameters in a session.",
    responses={
        **COMMON_ERRORS,
        status.HTTP_200_OK: {
            'model': dict,
            'description': 'Generated YAML configuration'
        }
    },
)
async def generate_ciq_yaml(session_id: str) -> dict:
    """Generate final YAML configuration from session parameters."""
    try:
        logger.info(f"Generating YAML for CIQ session: {session_id}")

        session = ciq_agent.session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )

        if not session.is_complete:
            raise HTTPException(
                status_code=400,
                detail="Session is not complete. Collect all parameters first."
            )

        if not session.final_yaml:
            # Generate YAML if not already generated
            session.final_yaml = ciq_agent._generate_final_yaml(session)
            ciq_agent.session_manager.update_session(session_id, session)

        logger.info(f"YAML generated successfully for session: {session_id}")

        return {
            "yaml_content": session.final_yaml,
            "session_id": session_id,
            "parameters_count": len(session.collected_values),
            "generated_at": session.last_activity
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating YAML: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate YAML: {str(e)}"
        )
