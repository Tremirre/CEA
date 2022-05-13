import enum


class Label(enum.Enum):
    POSITIVE = enum.auto()
    NEGATIVE = enum.auto()
    EMPTY = enum.auto()


attribute = str
value = str
