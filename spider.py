#!/usr/bin/env python3

import bs4
import pathlib
import re
import requests
import sys
from typing import Iterator
import urllib.parse

class Spider:

    def __init__(self) -> None:
        self.url = None
        self.recursive = False
        self.depth = 5
        self.path = "./data"
        self.visited = set[str]()
        self.to_visit = list[str]()

    def usage():
        print("Usage: spider [-r] [-p <path>] [-l <depth>] <url>", file=sys.stderr)

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

        if not self.recursive:
            self.depth = 1

        if self.url is None:
            raise Exception("missing url")

    URL_ROOT_REGEX = r"^(.+://.+)/?"

    def fix_url(base: str, href: str) -> str:
        return str(urllib.parse.urljoin(base, href))

    def visit_html(self, url: str, res: requests.Response):
        soup = bs4.BeautifulSoup(res.content, "html.parser")
        tags = soup.select("[href], [src]")

        for tag in tags:
            if (href := tag.get("href") or tag.get("src")) is None:
                continue

            new_url = Spider.fix_url(url, href)

            if new_url not in self.visited:
                self.to_visit.append(new_url)

    def visit_image(self, url: str, res: requests.Response):
        u = urllib.parse.urlparse(url)
        file_path = u.path.lstrip("/")
        out_path = pathlib.Path(self.path, urllib.parse.unquote(file_path))

        out_path.parent.mkdir(parents=True, exist_ok=True)


        with out_path.open("wb") as f:
            print(f"Downloading: {out_path}")
            for b in res.iter_content(chunk_size=None):
                f.write(b)
            print(f"Done")

    DEFAULT_CONTENT_TYPE = "text/plain"
    CONTENT_TYPE_REGEX = r"^([^;]+)"
    HTML_MIME_TYPES = {"text/html"}
    IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/gif", "image/bmp"}

    def get_mime_type(header: str | None) -> str:
        if header is None or (m := re.match(Spider.CONTENT_TYPE_REGEX, header)) is None:
            return Spider.DEFAULT_CONTENT_TYPE

        return m.group(1)

    def visit(self, url: str):
        if url in self.visited:
            return

        try:
            r = requests.get(url, allow_redirects=True, stream=True)
        except requests.exceptions.RequestException:
            return

        if not r.ok:
            return

        print(f"Visiting: {url}")

        content_type = Spider.get_mime_type(r.headers.get("Content-Type", None))

        self.visited.add(url)

        if content_type in Spider.HTML_MIME_TYPES:
            self.visit_html(url, r)
        elif content_type in Spider.IMAGE_MIME_TYPES:
            self.visit_image(url, r)

    def pre_run(self):
        p = pathlib.Path(self.path)
        p.mkdir(parents=False, exist_ok=False)

    def run(self):
        self.pre_run()

        self.to_visit.append(self.url)
        current_depth = 0

        while current_depth <= self.depth:
            count = len(self.to_visit)

            # no more pages to visit
            if count == 0:
                break

            while count > 0:
                url = self.to_visit.pop(0)
                self.visit(url)
                count -= 1
            current_depth += 1

def main(args: list[str]) -> int:
    spider = Spider()

    try:
        spider.parse_args(args[1:])
    except Exception as e:
        Spider.usage()
        print()
        print(f"spider: error: {e}", file=sys.stderr)
        return 1

    try:
        spider.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"spider: error: {e}", file=sys.stderr)
        raise e

    return 0

exit(main(sys.argv))
