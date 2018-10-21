from hyperwave import Source, TimeFrame


def func_check(args):
    print("============ Call check ==============")
    print(args)


def set_command(subparsers):
    download_parse = subparsers.add_parser("check",
                                           description="check if the symbol contain an hyperwave")
    download_parse.add_argument('--source', type=Source.from_string, choices=list(Source))
    download_parse.add_argument('--symbol', type=str, help="The synbol for which you want to download the data")

    download_parse.set_defaults(func=func_check)
