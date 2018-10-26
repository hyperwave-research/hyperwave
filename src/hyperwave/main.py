import argparse
import logging

from pandas.core.common import SettingWithCopyWarning

from ._commands import commands
import os
import pandas as pd

import warnings

warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

def get_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help="Set verbose mode")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-v", required=False, action='count', help="Set the logging mode to verbose")

    subparsers = parser.add_subparsers()

    for command in commands:
        command(subparsers, [parent_parser])
    return parser


def Main():

    parser = get_argparse()
    args = parser.parse_args()

    if args.v is not None:
        logging.basicConfig(level=logging.DEBUG)

    # Set pandas display for pretty print
    columns = 80
    rows = 50
    try:
        columns, rows = os.get_terminal_size()
    except:
        pass
    pd.set_option('display.max_rows', 1000)
    pd.set_option('display.max_columns', 999)
    pd.set_option('display.width', columns)
    pd.set_option('display.precision', 2)

    args.func(args)


if __name__ == "__main__":
    Main()
