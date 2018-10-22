import sys

from hyperwave import Main


def test_hw_command_parser(monkeypatch):
    arg_sample = ['main.py', 'download', '--source', 'Stooq', '--symbol', 'AAPL', '--output', '~ /spy.csv', '--timeframe',
                  'Weekly']

    monkeypatch.setattr(sys, 'argv', arg_sample)
    Main()