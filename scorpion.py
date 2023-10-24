#!/usr/bin/env python3

import sys
import PIL.Image
import PIL.ExifTags

def display_info(file_name: str):
    im = PIL.Image.open(file_name)

    print(f"{file_name}:")

    tags = im.getexif()

    if len(tags) == 0:
        print("no Exif metadata")
    else:
        for id, value in tags.items():
            if (name := PIL.ExifTags.TAGS.get(id, None)) is None:
                continue
            print(f"  [{name}] = {value}")
    print()

def main(argv: list[str]) -> int:
    args = argv[1:]

    if len(args) == 0:
        print("Usage: scorpion <files...>")
        exit(0)

    for file_name in args:
        display_info(file_name)

if __name__ == "__main__":
    exit(main(sys.argv))
