from pathlib import Path

import requests
import yaml


def get_download_config_file() -> dict:
    download_config_file = Path(__file__).parent / 'config' / 'download_config.yaml'
    with open(download_config_file, 'r') as in_file:
        return yaml.safe_load(in_file)


def get_zoom(download_config: dict) -> str:
    return download_config['zoom']


def get_size(download_config: dict) -> str:
    return download_config['size']


def get_scale(download_config: dict) -> str:
    return download_config['scale']


def get_map_type(download_config: dict) -> str:
    return download_config['map_type']


def get_api_key(download_config: dict) -> str:
    return download_config['api_key']


def download_satellite_image(center_lat: str, center_lon: str, output_path: Path, test=0) -> list:

    if not test:  # noqa:WPS504

        download_config = get_download_config_file()
        zoom = get_zoom(download_config)
        size = get_size(download_config)
        scale = get_scale(download_config)
        map_type = get_map_type(download_config)
        api_key = get_api_key(download_config)

        link = 'https://maps.googleapis.com/maps/api/staticmap?'
        url = f'{link}center={center_lat},{center_lon}&zoom={zoom}&size={size}x{size}&scale={scale}&maptype={map_type}&key={api_key}'
        # print('******************\n', url, '\n******************')
        response = requests.get(url)

        if response.status_code == 200:  # noqa:WPS432
            with open(output_path, 'wb') as out_file:
                out_file.write(response.content)
                return [zoom, size]
        else:
            print('Error:', response.status_code)
            return None
    else:
        print('Test mode')
    return None
