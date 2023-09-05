import requests
import os
import zipfile
import csv

ZIP_CODE_TAB_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2022_Gazetteer/2022_Gaz_zcta_national.zip"
CACHE_DIRECTORY_NAME = ".cache"
ZIP_CODE_TAB_NAME = "zipcode.zip"
ZIP_CODE_TAB_TSV_NAME = "2022_Gaz_zcta_national.txt"

CACHE_PATH = os.path.join(os.getcwd(), CACHE_DIRECTORY_NAME)
ZIP_CODE_TAB_ZIP_PATH = os.path.join(CACHE_PATH, ZIP_CODE_TAB_NAME)
ZIP_CODE_TAB_UNZIP_PATH = os.path.join(CACHE_PATH, "zipcode")
ZIP_CODE_TAB_TSV_PATH = os.path.join(ZIP_CODE_TAB_UNZIP_PATH, ZIP_CODE_TAB_TSV_NAME)


class LatLongZipcode:
    def __init__(self):
        self._load_data()

    def _load_data(self):
        self._download_data_if_no_cache()
        self._load_raw_data()
    
    def _download_data_if_no_cache(self):
        if not os.path.exists(CACHE_PATH):
            print("No cache found, creating cache...")
            os.makedirs(CACHE_PATH)
            with open(ZIP_CODE_TAB_ZIP_PATH, 'xb') as f:
                f.write(requests.get(ZIP_CODE_TAB_URL).content)
                print("Downloaded source zip") 
            with zipfile.ZipFile(ZIP_CODE_TAB_ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(ZIP_CODE_TAB_UNZIP_PATH)
                print("Unzipped source") 

    def _load_raw_data(self):
        self._raw_data = {}
        with open(ZIP_CODE_TAB_TSV_PATH, "r", newline="") as tsv_file:
            tsv_reader = csv.DictReader(tsv_file, delimiter='\t')
            for row in tsv_reader:      
                trimmed_row = {k.strip(): v.strip() for k, v in row.items()}
                zipcode = int(trimmed_row["GEOID"])
                filtered_row = {zipcode: {"lat": float(trimmed_row["INTPTLAT"]), "long":float(trimmed_row["INTPTLONG"]), "zipcode": zipcode}}
                self._raw_data.update(filtered_row)

    def to_zip(self, latitude, longtitude):
        return min(self._raw_data.items(), key=lambda item: abs(latitude - item[1]["lat"])**2 + abs(longtitude - item[1]["long"])**2)[0]

    def to_latlong(self, zipcode):
        item = self._raw_data[zipcode]
        return (item["lat"], item["long"])

        
def main():
    llzip = LagLongZipcode()
    print(llzip.to_zip(47.1183, -122.665))
    print(llzip.to_latlong(98516))
    
if __name__=="__main__":
    main()
    
