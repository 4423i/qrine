from .cross_join import CrossJoinRule
from .implicit_global import ImplicitGlobalRule
from .nested_each import NestedEachRule
from .reserved_word import ReservedWordRule
from .unused_var import UnusedVarRule
from .value_execution import ValueExecutionRule

RULES = [
    ReservedWordRule(),
    CrossJoinRule(),
    UnusedVarRule(),
    ImplicitGlobalRule(),
    NestedEachRule(),
    ValueExecutionRule(),
]
