"""
Tests package for WorkBuddy.
This package contains all unit and integration tests.
"""

# Import test modules
try:
    from tests.test_file_search import main as test_file_search
except ImportError:
    pass

try:
    from tests.test_search_navigator import main as test_search_navigator
except ImportError:
    pass

try:
    from tests.test_everything_search import main as test_everything_search
except ImportError:
    pass

try:
    from tests.test_search_for_file import main as test_search_for_file
except ImportError:
    pass

try:
    from tests.test_compare_search_methods import main as test_compare_search_methods
except ImportError:
    pass

try:
    from tests.test_real_file_search import main as test_real_file_search
except ImportError:
    pass

try:
    from tests.test_file_search_controller import main as test_file_search_controller
except ImportError:
    pass

try:
    from tests.test_command import run_shell_command
except ImportError:
    pass

try:
    from tests.test_calendar_manual import test_calendar_operations
except ImportError:
    pass
