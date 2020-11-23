from enum import Enum


class State(Enum):
    S_INITIAL = 1
    S_ADDING_NAME_TO_PLACE = 2
    S_ADDING_COORD_TO_PLACE = 3
    S_EMPTY = 4


class AnswerState(Enum):
    S_ERROR = 1
    S_OK = 2
