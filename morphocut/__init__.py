from ._version import get_versions
from .core import (
    LambdaNode,
    Node,
    Output,
    Pipeline,
    RawOrVariable,
    ReturnOutputs,
    Variable,
    closing_if_closable,
)

__version__ = get_versions()["version"]
del get_versions
