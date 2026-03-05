from .cross_join import CrossJoinRule
from .debug_print import DebugPrintRule
from .exit_in_function import ExitInFunctionRule
from .hopen_not_closed import HopenNotClosedRule
from .implicit_global import ImplicitGlobalRule
from .nested_each import NestedEachRule
from .peach_shared_state import PeachSharedStateRule
from .reval_usage import RevalUsageRule
from .reserved_word import ReservedWordRule
from .select_without_from import SelectWithoutFromRule
from .system_call import SystemCallRule
from .unused_var import UnusedVarRule
from .value_execution import ValueExecutionRule

RULES = [
    ReservedWordRule(),
    CrossJoinRule(),
    UnusedVarRule(),
    ImplicitGlobalRule(),
    NestedEachRule(),
    ValueExecutionRule(),
    DebugPrintRule(),
    ExitInFunctionRule(),
    SystemCallRule(),
    RevalUsageRule(),
    SelectWithoutFromRule(),
    HopenNotClosedRule(),
    PeachSharedStateRule(),
]
