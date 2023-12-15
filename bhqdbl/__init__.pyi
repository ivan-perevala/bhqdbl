
from typing import (
    Literal,
    TypedDict,
    Unpack,
    Callable,
    Sequence,
    NewType
)

from bpy.types import FloatProperty


class DoublePropertyKeywords(TypedDict):
    name: str
    description: str
    translation_context: str
    default: float
    min: float
    max: float
    soft_min: float
    soft_max: float
    step: int
    precision: int
    options: set[str]
    override: set[str]
    tags: set[str]
    subtype: str
    unit: str
    update: Callable
    get: Callable
    set: Callable


def double_property(
    attr_name: str,
    **kwargs: Unpack[DoublePropertyKeywords]
) -> tuple[property, FloatProperty]:
    ...


class DoubleArrayPropertyKeywords(TypedDict):
    name: str
    description: str
    translation_context: str
    default: Sequence[float]
    min: float
    max: float
    soft_min: float
    soft_max: float
    step: int
    precision: int
    options: set[str]
    override: set[str]
    tags: set[str]
    subtype: str
    unit: str
    size: int
    update: Callable
    get: Callable
    set: Callable


def double_array(
    attr_name: str,
    **kwargs: Unpack[DoubleArrayPropertyKeywords]
) -> tuple[property]:
    ...
