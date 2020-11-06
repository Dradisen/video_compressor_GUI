from enum import Enum

class CompressStatus(Enum):
    WAIT, PROCESS, COMPLETE, ERROR = range(4)