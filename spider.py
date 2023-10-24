#!/usr/bin/env python3

import sys
from typing import Iterator

class Spider:

    def __init__(self) -> None:
        self.url = None
        self.recursive = False
        self.depth = 5
        self.path = "./data"

    def get_option_parameter(it: Iterator[str], ch_it: Iterator[str], opt_ch: str) -> str:
        if (ch := next(ch_it, None)) is None: # option argument stop here
            if (param := next(it, None)) is None: # no argument after option argument
                raise Exception(f"option '{opt_ch}' requires an argument")
        else: # option argument is in the same argument as the option itself
            param = ch + "".join(ch_it)

        return param

    def parse_options_argument(self, it: Iterator[str], arg: str) -> None:
        """
        Parse options from a command-line argument, without the dash prefix

        ### Parameters
        - `it` an iterator over all the command-line arguments
        - `arg` current argument in `it`
        """
        chars = iter(arg)

        while (ch := next(chars, None)) is not None:
            match ch:
                case 'r':
                    self.recursive = True
                case 'l':
                    depth_arg = Spider.get_option_parameter(it, chars, ch)
                    depth = int(depth_arg)

                    if depth < 0:
                        raise ValueError(f"invalid negative number: {depth}")

                    self.depth = depth
                case 'p':
                    self.path = Spider.get_option_parameter(it, chars, ch)
                case _:
                    raise Exception(f"unknown option -- '{ch}'")

    def parse_args(self, args: list[str]) -> None:
        """
        Parse arguments from command-line, without the executable name
        """
        args_it = iter(args)

        while (arg := next(args_it, None)) is not None:

            if len(arg) > 1 and arg.startswith('-'):
                self.parse_options_argument(args_it, arg[1:])
            elif self.url is not None:
                raise Exception("too many url")
            else:
                self.url = arg

        if self.url is None:
            raise Exception("missing url")

def main(args: list[str]) -> int:
    spider = Spider()

    try:
        spider.parse_args(args[1:])
    except Exception as e:
        print(f"spider: error: {e}", file=sys.stderr)
        return 1

    print(f"url: {spider.url}")
    print(f"recursive: {spider.recursive}")
    print(f"depth: {spider.depth}")
    print(f"path: {spider.path}")

    return 0

exit(main(sys.argv))
