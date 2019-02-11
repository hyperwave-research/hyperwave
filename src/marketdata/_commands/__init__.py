from .download import set_command as download_set_command
from .download_index import set_command as download_index_command
from .split_assets import set_command as split_asset_command
from .resample import set_command as resample_command

commands = [download_set_command, download_index_command, split_asset_command, resample_command]
