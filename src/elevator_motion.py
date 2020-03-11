from enum import auto, Enum, unique


@unique
class ElevatorMotion(Enum):
    GETTING_FASTER = auto()  # at last step, the elevator was accelerating
    SLOWING = auto()  # at last step, the elevator was decelerating
    NEITHER = auto()  # at last step, the elevator was neither accelerating nor decelerating. So, the elevator could
    # have not started yet, or it could be at max velocity
