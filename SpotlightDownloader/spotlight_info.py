import json
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit, quote


def fetch_cn_spotlight_info(page_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the title and background image URL from a cn.bing.com URL of spotlight wallpaper.

    Args:
        page_url (str): The URL of the spotlight wallpaper to fetch the information from.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the title and background image URL.
    """
    try:
        response = requests.get(page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            heading_element = soup.find(id="heading-url")
            heading_text = heading_element.get_text() if heading_element else None

            bcg_img_element = soup.find(id="bcg-img-url")
            if bcg_img_element:
                style_attr = bcg_img_element.get("style", "")
                if 'background-image' in style_attr:
                    start = style_attr.find('url(') + 4
                    end = style_attr.find(')', start)
                    background_image_url = style_attr[start:end].strip("'\"")
                else:
                    background_image_url = None
            else:
                background_image_url = None
            return heading_text, background_image_url
        else:
            print(f"Failed to load the page. Status code: {response.status_code}")
            return None, None

    except requests.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        return None, None

@dataclass
class SpotlightInfo:
    """
    Data class to store information about a Windows spotlight wallpaper.

    Attributes:
        title (str): The title of the wallpaper.
        description (str): The description of the wallpaper.
        copyright (str): The copyright information of the wallpaper.
        edge_uri (str): The URI to open webpage about the wallpaper in Edge.
        _tracking_uri (str): The tracking URI.
        _local_path_landscape (str): The local path for the cache of landscape image.
        _local_path_portrait (str): The local path for the cache of portrait image.
    """
    title: str
    description: str
    copyright: str
    edge_uri: str
    _tracking_uri: str
    _local_path_landscape: str
    _local_path_portrait: str

    def url(self) -> str:
        """
        Returns the encoded URL of the wallpaper detail webpage.

        Returns:
            str: The URL of the wallpaper detail webpage.
        """
        parts = urlsplit(self.edge_uri.replace("microsoft-edge:", ""))
        return str(urlunsplit((
            parts.scheme, parts.netloc,
            quote(parts.path, safe="/"),
            quote(parts.query, safe="=&"),
            quote(parts.fragment)
        )))


def get_desktop_spotlight_info() -> Tuple[Optional[list[SpotlightInfo]], Optional[int]]:
    """
    Retrieves desktop spotlight wallpapers information from the Windows registry.

    Returns:
        Tuple[Optional[list[SpotlightInfo]], Optional[int]]:
            A tuple containing a list of SpotlightInfo objects and the current image index.
    """
    try:
        import winreg
    except ImportError:
        return None, None

    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\DesktopSpotlight\Creatives",
            0,
            winreg.KEY_READ
        )
        creatives_json, reg_type = winreg.QueryValueEx(registry_key, "Creatives")
        image_index, reg_type = winreg.QueryValueEx(registry_key, "ImageIndex")
        winreg.CloseKey(registry_key)

        creatives_raw = json.loads(creatives_json)
        creatives_data = [
            SpotlightInfo(
                title=creative.get("ad", {}).get("title"),
                description=creative.get("ad", {}).get("description"),
                copyright=creative.get("ad", {}).get("copyright"),
                edge_uri=creative.get("ad", {}).get("ctaUri"),
                _tracking_uri=creative.get("tracking", {}).get("baseUri"),
                _local_path_landscape=creative.get("ad", {}).get("landscapeImage", {}).get("asset"),
                _local_path_portrait=creative.get("ad", {}).get("portraitImage", {}).get("asset")
            ) for creative in creatives_raw
        ]

        return creatives_data, image_index

    except FileNotFoundError:
        print("Registry key or value not found.")
        return None, None
    except json.JSONDecodeError:
        print("The value of the Creatives key is not a valid JSON format.")
        return None, None
    except Exception as e:
        print(f"Error reading the registry: {e}")
        return None, None


def get_edge_uri_from_registry() -> Optional[str]:
    """
    Retrieves the URL of the current spotlight wallpaper from the Windows registry.

    Returns:
        Optional[str]: The Edge URI if found, otherwise None.
    """
    try:
        import winreg
    except ImportError:
        return None

    try:
        registry_key = winreg.OpenKey(
            winreg.HKEY_CLASSES_ROOT,
            r"CLSID\{2cc5ca98-6485-489a-920e-b3e88a6ccce3}\shell\SpotlightClick",
            0,
            winreg.KEY_READ
        )
        edge_uri, reg_type = winreg.QueryValueEx(registry_key, "EdgeUri")
        winreg.CloseKey(registry_key)

        return edge_uri.replace("microsoft-edge:", "")

    except FileNotFoundError:
        print("Registry key or value not found.")
        return None
    except Exception as e:
        print(f"Error reading the registry: {e}")
        return None