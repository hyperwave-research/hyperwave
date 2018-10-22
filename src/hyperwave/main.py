import argparse
import logging

from ._commands import commands


def get_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', help="Set verbose mode")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-v", action='count', help="Set the loggin mode to verbose")

    subparsers = parser.add_subparsers()

    for command in commands:
        command(subparsers, [parent_parser])
    return parser


def Main():
    parser = get_argparse()
    args = parser.parse_args()

    if args.v > 0:
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)


if __name__ == "__main__":
    Main()