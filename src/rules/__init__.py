from .cross_join import CrossJoinRule
from .debug_print import DebugPrintRule
from .delete_without_where import DeleteWithoutWhereRule
from .exit_in_function import ExitInFunctionRule
from .function_many_params import FunctionManyParamsRule
from .global_amend_in_function import GlobalAmendInFunctionRule
from .hopen_not_closed import HopenNotClosedRule
from .hopen_string_arg import HopenStringArgRule
from .implicit_global import ImplicitGlobalRule
from .nested_each import NestedEachRule
from .null_comparison import NullComparisonRule
from .overlong_line import OverlongLineRule
from .peach_shared_state import PeachSharedStateRule
from .protected_namespace import ProtectedNamespaceRule
from .reval_usage import RevalUsageRule
from .reserved_word import ReservedWordRule
from .select_without_from import SelectWithoutFromRule
from .shadow_global import ShadowGlobalRule
from .system_call import SystemCallRule
from .update_without_where import UpdateWithoutWhereRule
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
    NullComparisonRule(),
    ShadowGlobalRule(),
    OverlongLineRule(),
    GlobalAmendInFunctionRule(),
    HopenStringArgRule(),
    DeleteWithoutWhereRule(),
    UpdateWithoutWhereRule(),
    FunctionManyParamsRule(),
    ProtectedNamespaceRule(),
]
