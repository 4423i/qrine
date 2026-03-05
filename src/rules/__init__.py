from .cross_join import CrossJoinRule
from .implicit_global import ImplicitGlobalRule
from .nested_each import NestedEachRule
from .unused_var import UnusedVarRule
from .value_execution import ValueExecutionRule

RULES = [
    CrossJoinRule(),
    UnusedVarRule(),
    ImplicitGlobalRule(),
    NestedEachRule(),
    ValueExecutionRule(),
]
