from enum import Enum

class FileStatus(Enum):
    REQUESTED = 'REQ'
    UPLOADED = 'UPLOADED'
    DONE = 'DONE'
    ERROR = 'ERROR' 