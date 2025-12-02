"""Core orchestrator for Machine Spirit.

This module coordinates:
- Conversation handling
- Mode selection (DEV / OPS / STORY / ANALYST / etc.)
- Tool and cortex routing
- Integration with the SelfModel for stateful behaviour

At this stage it is a lightweight but fully functional skeleton:
it shows how requests flow through the system, logs key events
to the self_model, and prepares the ground for future expansion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal

from .self_model import SelfModel, EpistemicSnapshot


ConversationMode = Literal["default", "DEV", "OPS", "STORY", "ANALYST"]


@dataclass
class OrchestratorConfig:
    """Configuration for the Machine Spirit orchestrator."""

    default_mode: ConversationMode = "default"
    max_history_messages: int = 50
    enable_autonomy: bool = True


class MachineSpiritOrchestrator:
    """High–level coordinator for Machine Spirit.

    Responsibilities
    ----------------
    - Maintain lightweight conversation state per user/session
    - Route user messages through reasoning / knowledge / tools (to be plugged in)
    - Update the SelfModel with runtime, epistemic and behavioral signals
    - Provide a clear API for the REST / WebSocket layer (app/routes_chat.py)

    This class is intentionally written to be easy to extend: almost every
    logically distinct step is isolated into its own method.
    """

    def __init__(self, self_model: SelfModel, config: Optional[OrchestratorConfig] = None) -> None:
        self.self_model = self_model
        self.config = config or OrchestratorConfig()

        # In–memory conversation buffers: {session_id: [..messages..]}
        # In a real deployment this would likely be persisted or off‑loaded.
        self._conversations: Dict[str, List[Dict[str, Any]]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_message(
        self,
        session_id: str,
        user_id: str,
        text: str,
        mode: Optional[ConversationMode] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Main entry point for chat.

        Parameters
        ----------
        session_id:
            Conversation/session identifier.
        user_id:
            Logical user identifier.
        text:
            The raw user message.
        mode:
            Optional conversation mode (DEV / OPS / STORY / etc.).
        metadata:
            Optional extra context (timestamps, client info, etc.).

        Returns
        -------
        dict
            A response payload containing:
            - "reply": generated text reply
            - "mode": final mode used
            - "epistemic": confidence and sources summary
            - "self_state": lightweight snapshot of the self model
        """
        mode = mode or self.config.default_mode

        # 1) Register that we are active and update runtime state
        self.self_model.track_activity(user_id=user_id, session_id=session_id)
        self.self_model.set_current_mode(mode)

        # 2) Append user message to conversation history
        self._append_message(session_id, role="user", content=text, metadata=metadata or {})

        # 3) High‑level reasoning & routing (currently a stubbed pipeline)
        plan = self._draft_plan(text=text, mode=mode, session_id=session_id)
        tool_results = self._maybe_call_tools(plan=plan, session_id=session_id)
        reply_text, epistemic = self._generate_reply(
            text=text,
            plan=plan,
            tool_results=tool_results,
            mode=mode,
            session_id=session_id,
        )

        # 4) Store assistant reply
        self._append_message(session_id, role="assistant", content=reply_text, metadata={"mode": mode})

        # 5) Update epistemic snapshot in the self‑model
        self.self_model.update_epistemic_state(epistemic)

        # 6) Build response
        response: Dict[str, Any] = {
            "reply": reply_text,
            "mode": mode,
            "epistemic": epistemic.as_dict(),
            "self_state": self.self_model.to_lightweight_dict(),
        }

        return response

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _append_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any]) -> None:
        """Append a message to the in‑memory conversation buffer."""
        history = self._conversations.setdefault(session_id, [])
        history.append({"role": role, "content": content, "metadata": metadata})
        # Truncate history if needed
        max_h = self.config.max_history_messages
        if len(history) > max_h:
            del history[0 : len(history) - max_h]

    def _draft_plan(self, text: str, mode: ConversationMode, session_id: str) -> Dict[str, Any]:
        """Create a very simple 'plan' object for what to do with the message.

        In future this will call the reasoning cortex + knowledge retrieval,
        but even as a stub we keep the structure that those modules will
        populate later.
        """
        # For now we simply encode some metadata and a placeholder step.
        plan: Dict[str, Any] = {
            "mode": mode,
            "steps": [
                {
                    "type": "respond_directly",
                    "description": "Use the core text model to answer the user.",
                }
            ],
            "session_id": session_id,
        }

        # We notify the self‑model that a new plan was drafted (useful for analytics).
        self.self_model.log_event(
            event_type="plan_drafted",
            description=f"Drafted simple plan with mode={mode}",
            metadata={"session_id": session_id},
        )
        return plan

    def _maybe_call_tools(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Placeholder for tool / plugin execution.

        In later versions this will inspect the plan, call the tools from
        backend.tools.registry, and return their results. For now we simply
        return an empty structure while keeping the interface intact.
        """
        _ = (plan, session_id)  # unused, keep signature stable
        return {}

    def _generate_reply(
        self,
        text: str,
        plan: Dict[str, Any],
        tool_results: Dict[str, Any],
        mode: ConversationMode,
        session_id: str,
    ) -> tuple[str, EpistemicSnapshot]:
        """Generate the assistant's reply text and an epistemic snapshot.

        Today this is a simple echo‑style reply with some flavour, but the
        method is already shaped so you can plug in the real LLM, knowledge
        retrieval and creativity engines later without changing the external
        API.
        """
        _ = (plan, tool_results, session_id)  # placeholders for future use

        # Minimal example behaviour per mode
        if mode == "DEV":
            prefix = "[DEV] "
        elif mode == "OPS":
            prefix = "[OPS] "
        elif mode == "STORY":
            prefix = "[STORY] "
        elif mode == "ANALYST":
            prefix = "[ANALYST] "
        else:
            prefix = ""

        reply = f"{prefix}Machine Spirit has received: {text!r}. Real reasoning core not wired yet."

        # Basic epistemic snapshot: low confidence because this is stub logic.
        epistemic = EpistemicSnapshot(
            confidence="low",
            sources=["internal_stub"],
            notes="Using placeholder echo logic; no real model consulted yet.",
        )
        return reply, epistemic

    # ------------------------------------------------------------------
    # Convenience / introspection
    # ------------------------------------------------------------------

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Return the current in‑memory history for a session."""
        return list(self._conversations.get(session_id, []))

    def clear_conversation_history(self, session_id: str) -> None:
        """Clear a session's conversation buffer."""
        self._conversations.pop(session_id, None)
