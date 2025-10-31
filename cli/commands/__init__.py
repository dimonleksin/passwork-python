from .exec_command import ExecuteCommandStrategy
from .api_command import ApiCallStrategy
from .get_command import GetCommandStrategy
from .update_command import UpdateCommandStrategy

# Create a mapping of command names to strategy classes
COMMAND_STRATEGIES = {
    "exec": ExecuteCommandStrategy,
    "api": ApiCallStrategy,
    "get": GetCommandStrategy,
    "update": UpdateCommandStrategy
}
