import sys
from spotlight_info import *
from cli_utils import *
import argparse

def init_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A tool to download Windows spotlight wallpapers.")
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force download even if the file already exists."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="The output directory for the downloaded wallpaper."
    )
    parser.add_argument(
        "url",
        nargs="*",
        help="The URLs of the wallpaper detail webpage."
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="Lists the four wallpapers currently available in the Windows spotlight cache without download."
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Downloads all the wallpapers in the Windows spotlight cache."
    )
    return parser.parse_args()


if __name__ == '__main__':
    if os.name != "nt":
        print("This tool only works on Windows.")
        sys.exit(1)
    data, index = get_desktop_spotlight_info()
    if (data is None) or (index is None):
        print("Failed to retrieve spotlight information.")
        sys.exit(1)
    args = init_cli()
    if args.list:
        list_info(data, index)
    elif args.url:
        for url in args.url:
            filename = download_wallpaper(url, args.output, args.force)
            if filename:
                print(f"Downloaded to {filename}")
            else:
                print(f"Failed to download the wallpaper at {url}.")
    elif args.all:
        for i, info in enumerate(data):
            filename = download_wallpaper(info, args.output, args.force)
            if filename:
                print(f"Downloaded to {filename}")
            else:
                print(f"Failed to download the wallpaper {info.title}.")
    else:
        filename = download_wallpaper(data[index], args.output, args.force)
        if filename:
            print(f"Downloaded to {filename}")
        else:
            print(f"Failed to download the wallpaper {data[index].title}.")
else:
    pass