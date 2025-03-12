# Description: Download satellite images from Google Maps API for a given corridor
# and save them as GeoTIFF files.
from pathlib import Path

import geopandas as gpd
import rasterio as rio
import shapely
import yaml
from add_gps import calculate_area_extent, jpeg_to_geotiff
from downloads_staticmap_google import download_satellite_image


def sample_points(geometry: shapely.geometry.multilinestring.MultiLineString, step: float):
    points = []
    for line in geometry.geoms:
        length = line.length
        current_distance = 0
        while current_distance <= length:
            point = line.interpolate(current_distance)
            points.append((point.x, point.y))
            current_distance += step
    return points


def main():
    corridors_config_file = Path(__file__).parent / 'config' / 'corridors_config.yaml'
    with open(corridors_config_file, 'r') as in_file:
        corridors_config = yaml.safe_load(in_file)

    output_path = Path(__file__).parent / corridors_config['output_folder']

    to_download = 1
    tif_image = None
    for corridor in corridors_config['corridor_list']:
        print(corridor, corridors_config['corridor_list'][corridor])

        gdf = gpd.read_file(corridors_config['corridor_list'][corridor])

        jpg_path = output_path / f'{corridor}_corridor_jpg'
        jpg_path.mkdir(parents=True, exist_ok=True)

        tiff_path = output_path / f'{corridor}_corridor_tif'
        tiff_path.mkdir(parents=True, exist_ok=True)

        area_extent = calculate_area_extent()  # area_extent = circa 43 metri

        for idx, row in gdf.iterrows():
            # Campiona punti ogni 21 metri circa
            sampled_points = sample_points(row['geometry'], step=area_extent / 2)
            print(idx, 'OF', len(gdf), len(sampled_points))
            for (lon, lat) in sampled_points:
                if tif_image:
                    src = rio.open(tif_image)
                    bnd = src.bounds

                    if bnd.left < lon < bnd.right and bnd.bottom < lat < bnd.top:
                        to_download = 0
                    else:
                        to_download = 1

                if to_download:
                    download_satellite_image(
                        lat,
                        lon,
                        output_path=jpg_path / f'_{lat}_{lon}.png',
                        test=0,
                    )
                    jpeg_to_geotiff(jpg_path / f'_{lat}_{lon}.png', tiff_path / f'_{lat}_{lon}.tif', lat, lon, area_extent)
                    tif_image = tiff_path / f'_{lat}_{lon}.tif'
                break
            break


if __name__ == "__main__":
    main()
