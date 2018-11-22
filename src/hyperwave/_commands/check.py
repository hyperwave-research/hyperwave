import datetime
import os

from hyperwave import Source, TimeFrame, OhlcLoader, Hyperwave


def func_check(args):
    hw = Hyperwave.get_standard_hyperwave()
    df_raw_data = OhlcLoader.get_historical_data(args.symbol, args.source, time_frame=TimeFrame.Weekly)

    (df_hull_hyperwave, hw_phases_temp, hyperwave) =  hw.get_hyperwave(df_raw_data)

    if args.outputType == 'display':
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    elif args.outputType == 'file':
        output_path = args.outputPath
        if not os.path.exists(output_path ):
            print ("The path {} doesn't exist. Please select a valid outputPath".format(output_path))

        file_name = "{}_{}_{:%Y%m%d}".format(args.source, args.symbol, datetime.datetime.now())
        raw_data_file_name = "{}.csv".format(file_name)
        hull_file_name = "{}.hull.csv".format(file_name)
        hw_file_name = "{}.hw.csv".format(file_name)

        df_raw_data.to_csv(os.path.join(output_path, raw_data_file_name), columns=['date', 'close', 'high', 'low', 'open'], index=False, header=True)
        df_hull_hyperwave.to_csv(os.path.join(output_path, hull_file_name ), header=True, index=False)
        hyperwave.to_csv(os.path.join(output_path, hw_file_name), header=True, index=False)


def set_command(subparsers, parents):
    check_parser = subparsers.add_parser("check", parents=parents,
                                           description="check the given symbol is on Hyperwave")
    check_parser.add_argument('--source', type=Source.from_string, choices=list(Source))
    check_parser.add_argument('--symbol', type=str, help="The synbol for which you want to download the data")
    check_parser.add_argument('--outputType', type=str,choices=["display", "file"], default="display", help="Set the output source. Default display")
    check_parser.add_argument('--outputPath', type=str, default='.', help="Path to the folder where we persist the result")

    check_parser.set_defaults(func=func_check)
