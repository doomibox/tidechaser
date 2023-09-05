import requests
import pprint
import argparse
from datetime import datetime
from llzip import LatLongZipcode

pp = pprint.PrettyPrinter(indent=4)
llzip = LatLongZipcode()

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT= "{} {}".format(DATE_FORMAT, TIME_FORMAT)
API = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'
STATION_API = 'https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=tidepredictions'

API_PARAM_TEMPLATE = {
    "begin_date": "",
    "end_date": "", 
    "station": "9446828",
    "application": "NOS.COOPS.TAC.TidePred", 
    "datum": "MLLW", 
    "format": "json",
    "interval": "hilo",
    "product": "predictions",
    "time_zone": "lst_ldt", 
    "units": "english", 
}


def fetch_tide_predictions(begin_date, end_date, station):
    api_param = generate_api_param(begin_date, end_date, station)
    return requests.get(API, params=api_param).json()['predictions']

def fetch_tide_station(zipcode):
    stations = requests.get(STATION_API).json()['stations']
    ziplat, ziplng = llzip.to_latlong(zipcode)
    return min(stations, key=lambda s: abs(s["lat"] - ziplat)**2 + abs(s['lng'] - ziplng)**2)

def generate_api_param(begin_date, end_date, station):
    api_param = dict(API_PARAM_TEMPLATE)
    api_param["begin_date"] = begin_date
    api_param["end_date"] = end_date
    api_param["station"] = station
    return api_param

def filter_tides(tide_predictions, tide_fn):
    return list(filter(lambda tide: tide_fn(float(tide["v"])), tide_predictions))

def filter_time(tide_predictions, start_time="00:00", end_time="23:59"):
    start_time = datetime.strptime(start_time, TIME_FORMAT).time()
    end_time = datetime.strptime(end_time, TIME_FORMAT).time()
    return list(filter(lambda tide: get_time(tide) >= start_time and get_time(tide) <= end_time, tide_predictions))

def filter_weekday(tide_predictions, weekdays="1234567"):
    return list(filter(lambda tide: str(get_weekday(tide)) in weekdays, tide_predictions))

def get_datetime(tide):
    return datetime.strptime(tide["t"], DATETIME_FORMAT)

def get_time(tide):
    return get_datetime(tide).time()
    
def get_weekday(tide):
    return get_datetime(tide).weekday() + 1 # Monday is 1

def get_args():
    parser = argparse.ArgumentParser(description='Fetch tide info')
    parser.add_argument("begin_date")
    parser.add_argument("end_date")
    parser.add_argument("-s", "--start_time", default="00:00")
    parser.add_argument("-e", "--end_time", default="23:59")
    parser.add_argument("-t", "--low_tide", default=0.0, type=float) 
    parser.add_argument("-d", "--weekdays", default="1234567")
    parser.add_argument("-z", "--zipcode", default=98101, type=int)
    return parser.parse_args()

def _print_args(args):
    print("\nEvaluating with params:")
    varsargs = vars(args)
    for k in ["begin_date", "end_date", "zipcode", "start_time", "end_time", "low_tide", "weekdays"]:
        print("\t{}:\t{}".format(k, varsargs[k]))
    print()

def _print_station(station, zipcode):
    print("\nUsing data from station [{}] \"{}\" for {}:".format(station["id"], station["name"], zipcode))

def _print_tides(tides):
    # TODO: use pandas for better formatting
    header = "{}\t{}".format("Time".ljust(16, " "), "Tide(ft)") # 16 = len("2023-01-01 00:00")
    print("\n" + header)
    print("=" * (len(header) + 8)) # 8 = 1 tab size
    for t in tides:
        print("{}\t{}".format(t["t"], t["v"]))

def main(args):
    _print_args(args)
    station = fetch_tide_station(args.zipcode)
    _print_station(station, args.zipcode)

    tides = fetch_tide_predictions(args.begin_date, args.end_date, station["id"])
    tides = filter_tides(tides, lambda tide: tide <= args.low_tide)
    tides = filter_weekday(tides, args.weekdays)
    tides = filter_time(tides, start_time=args.start_time, end_time=args.end_time)
    _print_tides(tides)
    
if __name__=='__main__':
    main(get_args())
