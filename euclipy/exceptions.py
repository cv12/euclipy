class InconsistentValues(Exception):
    def __init__(self, cause) -> None:
        super().__init__(cause)

class InformationError(Exception):
    def __init__(self, cause) -> None:
        super().__init__(cause)