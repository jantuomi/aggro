from dataclasses import dataclass


@dataclass
class MemoryState:
    """MemoryState is a singleton class used for communicating between threads."""

    running: bool


memory_state = MemoryState(running=False)
