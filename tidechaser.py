import requests
import pprint
import argparse
from datetime import datetime


pp = pprint.PrettyPrinter(indent=4)

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT= "{} {}".format(DATE_FORMAT, TIME_FORMAT)
API = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter'

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
    parser.add_argument("-t", "--low_tide", type=float, default=0.0)
    parser.add_argument("-d", "--weekdays", default="1234567")
    return parser.parse_args()
    

def main(args):
    print(args)
    tides = fetch_tide_predictions(args.begin_date, args.end_date, '9446828')
    tides = filter_tides(tides, lambda tide: tide <= args.low_tide)
    tides = filter_weekday(tides, args.weekdays)
    tides = filter_time(tides, start_time=args.start_time, end_time=args.end_time)
    pp.pprint(tides)
    
if __name__=='__main__':
    main(get_args())
