class ClassroomNotFoundException(Exception):
    def __init__(self, message: str='Classroom not found'):
        super().__init__(message)