import os
from functools import singledispatch
from typing import Union, List, Optional
import requests
from spotlight_info import SpotlightInfo, fetch_cn_spotlight_info



@singledispatch
def download_wallpaper(info: Union[str, SpotlightInfo], path: str, force: bool) -> Optional[str]:
    """
    Downloads a spotlight wallpaper to the specified path.

    Args:
        info (Union[str, SpotlightInfo]): The URL of the wallpaper detail webpage or a SpotlightInfo object.
        path (str): The local path where the wallpaper will be saved.
        force (bool): If True, forces the download even if the file already exists.

    Returns:
        Optional[str]: The path where the wallpaper is saved, or None if the download fails.
    """
    pass

@download_wallpaper.register
def _(url: str, path: str, force: bool) -> Optional[str]:
    title, uri = fetch_cn_spotlight_info(url)
    server = url.split("/")[2]
    image_url = f"https://{server}{uri}"
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            extname = response.headers['Content-Type'].split("/")[-1]
            filename = os.path.isdir(path) and os.path.join(path, title + "." + extname) or path

            if os.path.exists(filename) and not force:
                print(f"File {filename} already exists. Use -f to force download.")
                return
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"Failed to download the image. Status code: {response.status_code}")
            return

    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
    return

@download_wallpaper.register
def _(info: SpotlightInfo, path: str, force: bool) -> Optional[str]:
    return download_wallpaper(info.edge_uri.replace("microsoft-edge:", ""), path, force)

def list_info(infos: List[SpotlightInfo], current: int) -> None:
    """
    Lists the titles and descriptions of SpotlightInfo objects, highlighting the current one.

    Args:
        infos (List[SpotlightInfo]): A list of SpotlightInfo objects.
        current (int): The index of the current SpotlightInfo object.
    """
    for i, info in enumerate(infos):
        if i == current:
            print(f"{i + 1}. {info.title} (current)")
        else:
            print(f"{i + 1}. {info.title}")
        print(f"   {info.description}")
