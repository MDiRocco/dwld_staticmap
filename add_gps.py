import os
from pathlib import Path

import numpy as np
import yaml
from downloads_staticmap_google import (get_download_config_file, get_size,
                                        get_zoom)
from osgeo import gdal, osr
from PIL import Image


def calculate_area_extent():
    zoom = get_zoom(get_download_config_file())
    size = get_size(get_download_config_file())
    return (360 / 2**zoom) * (size / 256)  # noqa:WPS432


def jpeg_to_geotiff(jpeg_path, tiff_path, center_lat, center_lon, area_extent):
    # Apri l'immagine e ottieni dimensioni
    img = Image.open(jpeg_path).convert("RGB")
    width, height = img.size

    pixel_size = area_extent / width

    # Calculate the coordinates of the bounding box
    xmin = center_lon - (width / 2) * pixel_size
    # xmax = center_lon + (width / 2) * pixel_size
    # ymin = center_lat - (height / 2) * pixel_size
    ymax = center_lat + (height / 2) * pixel_size

    img_array = np.array(img)

    # Create new file TIFF
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(tiff_path, width, height, 3 if len(img_array.shape) == 3 else 1, gdal.GDT_Byte, options=['COMPRESS=DEFLATE'])
    geotransform = [xmin, pixel_size, 0, ymax, 0, -pixel_size]
    dataset.SetGeoTransform(geotransform)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # WGS84 # noqa:WPS432
    dataset.SetProjection(srs.ExportToWkt())

    for count, _ in enumerate(img_array.shape):
        dataset.GetRasterBand(count + 1).WriteArray(img_array[:, :, count])

    dataset.FlushCache()
    dataset = None
    print(f"File TIFF salvato: {tiff_path}")


def run():
    base_path = Path(__file__).parent

    add_gps_config_file = base_path / 'config' / 'add_gps_config.yaml'
    with open(add_gps_config_file, 'r') as in_file:
        add_gps_config = yaml.safe_load(in_file)

    area_extent = calculate_area_extent()

    corridor_list = add_gps_config['corridor_list']
    for corridor in corridor_list:
        print(corridor, corridor_list[corridor]['data_path'])
        path_folder = Path(add_gps_config['output_folder']) / corridor_list[corridor]['data_path']
        output_corridor_folder_name = corridor_list[corridor]['data_path']
        tif_folder = base_path / add_gps_config['output_folder'] / f'{output_corridor_folder_name}_tif'
        tif_folder.mkdir(parents=True, exist_ok=True)

        for image in os.listdir(path_folder):
            if image.endswith('.png'):
                input_file = path_folder / image
                center_lat = float(input_file.stem.split('_')[0])
                center_lon = float(input_file.stem.split('_')[1])
                output_file = tif_folder / (image.replace('.png', '.tif'))
                jpeg_to_geotiff(input_file, output_file, center_lat=center_lat, center_lon=center_lon, area_extent=area_extent)
