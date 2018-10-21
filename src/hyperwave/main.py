import argparse
from ._commands import commands


def get_argparse():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for command in commands:
        command(subparsers)
    return parser


def Main():
    parser = get_argparse()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    Main()
