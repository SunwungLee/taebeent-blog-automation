from .config import (
    KW_STATUS_COLLECTED, KW_STATUS_APPROVED, KW_STATUS_GEN_REQUESTED,
    KW_STATUS_GENERATING, KW_STATUS_HTML_READY, KW_STATUS_READY_TO_PUBLISH,
    KW_STATUS_PUBLISHING, KW_STATUS_PUBLISHED, KW_STATUS_TRACKING,
    KW_STATUS_NEEDS_REFRESH
)

class StateTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    pass

# Allowed transitions for Keywords
ALLOWED_KW_TRANSITIONS = {
    KW_STATUS_COLLECTED: [KW_STATUS_APPROVED],
    KW_STATUS_APPROVED: [KW_STATUS_GEN_REQUESTED],
    KW_STATUS_GEN_REQUESTED: [KW_STATUS_GENERATING],
    KW_STATUS_GENERATING: [KW_STATUS_HTML_READY, KW_STATUS_APPROVED], # Can revert on failure
    KW_STATUS_HTML_READY: [KW_STATUS_READY_TO_PUBLISH],
    KW_STATUS_READY_TO_PUBLISH: [KW_STATUS_PUBLISHING],
    KW_STATUS_PUBLISHING: [KW_STATUS_PUBLISHED, KW_STATUS_READY_TO_PUBLISH], # Can revert on failure
    KW_STATUS_PUBLISHED: [KW_STATUS_TRACKING],
    KW_STATUS_TRACKING: [KW_STATUS_NEEDS_REFRESH],
    KW_STATUS_NEEDS_REFRESH: [KW_STATUS_GEN_REQUESTED]
}

def validate_kw_transition(current_status: str, next_status: str):
    """
    Validates if a transition from current_status to next_status is allowed.
    Raises StateTransitionError if invalid.
    """
    if current_status == next_status:
        return
    
    allowed = ALLOWED_KW_TRANSITIONS.get(current_status, [])
    if next_status not in allowed:
        raise StateTransitionError(
            f"Invalid keyword status transition: {current_status} -> {next_status}"
        )

def is_regeneration_allowed(status: str) -> bool:
    """
    Returns True if content regeneration is allowed for the given status.
    Python code must never regenerate content for items already in state-driven restricted list.
    """
    restricted = [
        KW_STATUS_GEN_REQUESTED,
        KW_STATUS_GENERATING,
        KW_STATUS_HTML_READY,
        KW_STATUS_READY_TO_PUBLISH,
        KW_STATUS_PUBLISHED
    ]
    return status not in restricted
