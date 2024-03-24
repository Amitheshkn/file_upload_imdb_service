from enum import Enum


class Collection(Enum):
    USERS = "users"
    MOVIES = "movies"
    FILE_PROCESS = "file_process"


class FileStatus:
    IN_PROGRESS = "in_progress"
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
