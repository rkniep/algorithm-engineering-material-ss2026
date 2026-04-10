from .first_improvement import first_improvement_two_opt
from .full_scan import full_scan_two_opt
from .best_improvement import best_improvement_two_opt

try:
    from ._core import (
        cpp_first_improvement,
        cpp_full_scan,
        cpp_best_improvement,
        parallel_two_opt,
    )
except ModuleNotFoundError as exc:
    if exc.name != "tsp_two_opt._core":
        raise
