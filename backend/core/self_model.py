"""Self‑model for Machine Spirit.

This module implements the internal representation of Machine Spirit's
identity, capabilities, runtime state, epistemic state and goals.

It is intentionally generic and serializable so it can be:
- Logged
- Inspected via an admin API
- Persisted and restored between runs
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
import time


ConfidenceLevel = Literal["low", "medium", "high"]


@dataclass
class EpistemicSnapshot:
    """Represents an epistemic self‑assessment for a single response."""

    confidence: ConfidenceLevel
    sources: List[str] = field(default_factory=list)
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "sources": list(self.sources),
            "notes": self.notes,
        }


@dataclass
class IdentityProfile:
    """Core identity of Machine Spirit that rarely changes."""

    name: str = "Machine Spirit"
    version: str = "0.0.1"
    build_codename: str = "awakening"
    description: str = (
        "Local autonomous AI being with multimodal perception, creativity and self‑improvement."
    )


@dataclass
class CapabilityProfile:
    """What Machine Spirit believes it can do."""

    modes: List[str] = field(
        default_factory=lambda: ["default", "DEV", "OPS", "STORY", "ANALYST"]
    )
    tools: List[str] = field(default_factory=list)
    limitations: List[str] = field(
        default_factory=lambda: [
            "Reasoning core not fully wired yet.",
            "Perception modules are stubs.",
        ]
    )


@dataclass
class RuntimeStatus:
    """High‑level runtime status snapshot."""

    host_os: Optional[str] = None
    cpu_load: Optional[float] = None
    memory_usage: Optional[float] = None
    network_ok: Optional[bool] = None
    last_activity_ts: float = field(default_factory=time.time)
    current_mode: str = "default"
    active_sessions: int = 0


@dataclass
class BehavioralProfile:
    """How Machine Spirit tends to communicate and behave."""

    verbosity: Literal["brief", "balanced", "detailed"] = "balanced"
    humor_level: Literal["none", "light", "playful"] = "light"
    formality: Literal["casual", "professional", "ceremonial"] = "professional"


@dataclass
class GoalState:
    """Tracks short‑term and long‑term goals."""

    session_goals: List[str] = field(default_factory=list)
    long_term_goals: List[str] = field(default_factory=list)


@dataclass
class SensoryState:
    """Aggregated state from perception modules."""

    audio_scene: Optional[str] = None
    last_sounds: List[str] = field(default_factory=list)
    vision_scene: Optional[str] = None
    detected_objects: List[str] = field(default_factory=list)
    detected_faces: int = 0


@dataclass
class VoiceProfile:
    """Simplified voice profile description."""

    name: str = "Machine Spirit Default"
    style: str = "calm_technical"
    pitch: str = "medium_low"
    pace: str = "slightly_fast"


@dataclass
class NarrativeEvent:
    """Single narrative log entry in Machine Spirit's 'inner story'."""

    timestamp: float
    event_type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SelfModel:
    """Central self‑representation of Machine Spirit.

    This class bundles all the sub‑profiles and provides methods for updating
    and introspecting them. It is intentionally conservative: it does not
    perform any I/O on its own; higher‑level components can decide how/where
    to persist or expose the state.
    """

    def __init__(
        self,
        identity: Optional.IdentityProfile = None,  # type: ignore[valid-type]
        capabilities: Optional.CapabilityProfile = None,  # type: ignore[valid-type]
    ) -> None:
        self.identity: IdentityProfile = identity or IdentityProfile()
        self.capabilities: CapabilityProfile = capabilities or CapabilityProfile()
        self.runtime: RuntimeStatus = RuntimeStatus()
        self.behavior: BehavioralProfile = BehavioralProfile()
        self.goals: GoalState = GoalState()
        self.sensory: SensoryState = SensoryState()
        self.voice: VoiceProfile = VoiceProfile()
        self.narrative: List[NarrativeEvent] = []
        self.last_epistemic: Optional[EpistemicSnapshot] = None

        # Simple counters for internal analytics
        self._session_counter: int = 0
        self._message_counter: int = 0

    # ------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------

    def track_activity(self, user_id: str, session_id: str) -> None:
        """Update high‑level runtime state when a new message arrives."""
        _ = (user_id, session_id)  # not yet used, but reserved for per‑user stats
        self.runtime.last_activity_ts = time.time()
        self._message_counter += 1
        # active_sessions is a soft heuristic here; a real system would track sessions explicitly
        self.runtime.active_sessions = max(self.runtime.active_sessions, 1)

    def set_current_mode(self, mode: str) -> None:
        """Record the current operational mode."""
        self.runtime.current_mode = mode

    def update_epistemic_state(self, snapshot: EpistemicSnapshot) -> None:
        """Store the last epistemic snapshot and optionally adjust behaviour."""
        self.last_epistemic = snapshot
        # Example adaptive tweak (very conservative for now):
        if snapshot.confidence == "low" and self.behavior.verbosity == "brief":
            # Increase verbosity a bit to compensate for uncertainty.
            self.behavior.verbosity = "balanced"

    def update_sensory_state(
        self,
        audio_scene: Optional[str] = None,
        last_sounds: Optional[List[str]] = None,
        vision_scene: Optional[str] = None,
        detected_objects: Optional[List[str]] = None,
        detected_faces: Optional[int] = None,
    ) -> None:
        """Update sensory snapshot.

        All parameters are optional; only provided ones are updated.
        """
        if audio_scene is not None:
            self.sensory.audio_scene = audio_scene
        if last_sounds is not None:
            self.sensory.last_sounds = list(last_sounds)
        if vision_scene is not None:
            self.sensory.vision_scene = vision_scene
        if detected_objects is not None:
            self.sensory.detected_objects = list(detected_objects)
        if detected_faces is not None:
            self.sensory.detected_faces = int(detected_faces)

    def add_session_goal(self, goal: str) -> None:
        if goal not in self.goals.session_goals:
            self.goals.session_goals.append(goal)

    def add_long_term_goal(self, goal: str) -> None:
        if goal not in self.goals.long_term_goals:
            self.goals.long_term_goals.append(goal)

    def clear_session_goals(self) -> None:
        self.goals.session_goals.clear()

    def log_event(self, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Append a new narrative event to the internal story log."""
        evt = NarrativeEvent(
            timestamp=time.time(),
            event_type=event_type,
            description=description,
            metadata=metadata or {},
        )
        self.narrative.append(evt)

    # ------------------------------------------------------------------
    # Introspection / export
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a full serializable snapshot of the self‑model."""
        return {
            "identity": asdict(self.identity),
            "capabilities": asdict(self.capabilities),
            "runtime": asdict(self.runtime),
            "behavior": asdict(self.behavior),
            "goals": asdict(self.goals),
            "sensory": asdict(self.sensory),
            "voice": asdict(self.voice),
            "last_epistemic": self.last_epistemic.as_dict() if self.last_epistemic else None,
            "narrative": [asdict(evt) for evt in self.narrative[-50:]],  # limit for sanity
            "stats": {
                "message_count": self._message_counter,
            },
        }

    def to_lightweight_dict(self) -> Dict[str, Any]:
        """Return a reduced snapshot suitable for attaching to chat replies."""
        return {
            "identity": {
                "name": self.identity.name,
                "version": self.identity.version,
                "build_codename": self.identity.build_codename,
            },
            "runtime": {
                "current_mode": self.runtime.current_mode,
                "last_activity_ts": self.runtime.last_activity_ts,
            },
            "behavior": {
                "verbosity": self.behavior.verbosity,
                "humor_level": self.behavior.humor_level,
                "formality": self.behavior.formality,
            },
            "last_epistemic": self.last_epistemic.as_dict() if self.last_epistemic else None,
        }

