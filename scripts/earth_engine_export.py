"""Earth Engine export: Sentinel-2 RGB + NDVI (2018, 2024) and Hansen forest loss.

Data-acquisition step of the pipeline. Exports GeoTIFFs to Google Drive; download them
into data/study_region/ before running the notebook's change-detection cells.

Setup (one time):
    pip install earthengine-api geemap
    earthengine authenticate
Set PROJECT below to your Earth Engine Cloud project ID, then run:
    python scripts/earth_engine_export.py
"""
import ee

PROJECT = "ml-deforestation"
BBOX    = [-123.4, 46.8, -122.9, 47.2]
YEAR_1, YEAR_2 = 2018, 2024
SCALE   = 10
FOLDER  = "deforestation"


def s2_rgb(region, year):
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
           .filterBounds(region).filterDate(f"{year}-06-01", f"{year}-09-15")
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
           .select(["B4", "B3", "B2"]))
    return col.median().clip(region)


def s2_ndvi(region, year):
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
           .filterBounds(region).filterDate(f"{year}-06-01", f"{year}-09-15")
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
           .select(["B8", "B4"]))
    return col.median().normalizedDifference(["B8", "B4"]).rename("NDVI").clip(region)


def export(image, name, region):
    ee.batch.Export.image.toDrive(
        image=image, description=name, folder=FOLDER,
        region=region, scale=SCALE, maxPixels=int(1e13)).start()
    print("export started:", name)


def main():
    ee.Initialize(project=PROJECT)
    region = ee.Geometry.Rectangle(BBOX)
    for year in (YEAR_1, YEAR_2):
        export(s2_rgb(region, year).visualize(min=0, max=3000), f"s2_rgb_{year}", region)
        export(s2_ndvi(region, year), f"ndvi_{year}", region)
    hansen = ee.Image("UMD/hansen/global_forest_change_2023_v1_11").select("lossyear").clip(region)
    export(hansen, "hansen_lossyear", region)
    print("Submitted. Track at https://code.earthengine.google.com/tasks")
    print("Download the GeoTIFFs from Google Drive into data/study_region/")


if __name__ == "__main__":
    main()
