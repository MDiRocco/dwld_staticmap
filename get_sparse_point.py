from pathlib import Path

import pandas as pd
import yaml
from downloads_staticmap_google import download_satellite_image


def extract_and_download() -> list:
    sparse_points_config_file = Path(__file__).parent / 'config' / 'sparse_points_config.yaml'
    with open(sparse_points_config_file, 'r') as in_file:
        sparse_points_config = yaml.safe_load(in_file)

    base = Path(__file__).parent
    points_folder = Path(sparse_points_config['points_folder'])

    files = sparse_points_config['corridors_data']

    for key_el in files:
        print(key_el)

        df_spot = pd.read_csv(points_folder / files[key_el]['csv_spot'])
        df_phr = pd.read_csv(points_folder / files[key_el]['csv_phr'])
        df = pd.concat([df_spot, df_phr])
        print(df.shape)

        point_list = df['coords'].tolist()
        for idx, point in enumerate(point_list):
            print(idx)
            lon, lat = point.split('_')

            output_folder = Path(sparse_points_config['output_folder']) / files[key_el]['output']
            output_folder.mkdir(parents=True, exist_ok=True)
            output_path = base / output_folder
            download_satellite_image(
                lat,
                lon,
                output_path=output_path / f'{lat}_{lon}.png',
                test=0,
            )


if __name__ == '__main__':
    extract_and_download()
