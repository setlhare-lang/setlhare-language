class SetlhareError(Exception):
    """Base error for Setlhare tooling."""


class SetlhareSyntaxError(SetlhareError):
    pass


class SetlhareRuntimeError(SetlhareError):
    pass


class ImmutableAssignmentError(SetlhareRuntimeError):
    pass
