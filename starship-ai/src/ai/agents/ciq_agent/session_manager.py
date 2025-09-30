# Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
#
# Session management for CIQ chat conversations
#

import time
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional, Set

from .config import DEFAULT_SESSION_CONFIG, PARAM_DESCRIPTIONS


@dataclass
class CIQChatMessage:
    """Represents a single chat message in a CIQ session."""

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class CIQSession:
    """Represents a CIQ chat session with parameter collection state."""

    session_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

    # Chat history
    messages: List[CIQChatMessage] = field(default_factory=list)

    # Parameter collection state
    collected_values: Dict[str, str] = field(default_factory=dict)
    missing_params: Set[str] = field(
        default_factory=lambda: set(PARAM_DESCRIPTIONS.keys())
    )
    current_param: Optional[str] = None

    # Session status
    is_complete: bool = False
    final_yaml: Optional[str] = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        self.messages.append(CIQChatMessage(role=role, content=content))
        self.last_activity = time.time()

    def collect_parameter(self, param: str, value: str) -> None:
        """Collect a parameter value and update session state."""
        self.collected_values[param] = value
        self.missing_params.discard(param)
        self.last_activity = time.time()

        # Set next parameter or mark as complete
        if self.missing_params:
            self.current_param = sorted(self.missing_params)[0]
        else:
            self.current_param = None
            self.is_complete = True

    def get_progress(self) -> Dict[str, any]:
        """Get current collection progress."""
        total_params = len(PARAM_DESCRIPTIONS)
        collected_count = len(self.collected_values)

        return {
            "total_params": total_params,
            "collected_count": collected_count,
            "progress_percentage": (collected_count / total_params) * 100,
            "missing_params": list(self.missing_params),
            "current_param": self.current_param,
            "is_complete": self.is_complete
        }

    def is_expired(
        self,
        max_duration: int = DEFAULT_SESSION_CONFIG["max_session_duration"]
    ) -> bool:
        """Check if session has expired."""
        return (time.time() - self.last_activity) > max_duration


class CIQSessionManager:
    """Manages multiple CIQ chat sessions."""

    def __init__(self):
        self._sessions: Dict[str, CIQSession] = {}
        self._lock = Lock()

    def create_session(self) -> str:
        """Create a new CIQ session and return session ID."""
        session_id = str(uuid.uuid4())

        with self._lock:
            session = CIQSession(session_id=session_id)
            # Initialize with first parameter
            if session.missing_params:
                session.current_param = sorted(session.missing_params)[0]

            # Add welcome message
            session.add_message(
                "assistant",
                "Hi! I'm your CIQ Assistant. I'll help you configure "
                "CMM deployment parameters step by step. Let's begin!"
            )

            self._sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str) -> Optional[CIQSession]:
        """Get session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def update_session(self, session_id: str, session: CIQSession) -> None:
        """Update session in manager."""
        with self._lock:
            self._sessions[session_id] = session

    def delete_session(self, session_id: str) -> bool:
        """Delete session by ID."""
        with self._lock:
            return self._sessions.pop(session_id, None) is not None

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of removed sessions."""
        expired_sessions = []

        with self._lock:
            for session_id, session in self._sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self._sessions[session_id]
        return len(expired_sessions)

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        with self._lock:
            return len(self._sessions)

    def get_or_create_session(
        self,
        session_id: Optional[str] = None
    ) -> tuple[str, CIQSession]:
        """Get existing session or create new one if not found."""
        if session_id:
            session = self.get_session(session_id)
            if session and not session.is_expired():
                return session_id, session

        # Create new session if none exists or expired
        new_session_id = self.create_session()
        new_session = self.get_session(new_session_id)
        return new_session_id, new_session


# Global session manager instance
session_manager = CIQSessionManager()
