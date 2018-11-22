
from .download import set_command as download_set_command
from .check import set_command as check_set_command
from .check_index import set_command as check_index_command

commands = [
    download_set_command,
    check_set_command,
    check_index_command
]
