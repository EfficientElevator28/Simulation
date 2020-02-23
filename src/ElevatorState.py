from enum import auto, Enum, unique


@unique
class ElevatorState(Enum):
    NO_ACTION = auto()  # elevator is not receiving any commands
    UP = auto()
    DOWN = auto()
    LOADING_UNLOADING = auto()  # elevator is opening, closing, or loading/unloading
