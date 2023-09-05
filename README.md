# Tide Chaser: CLI for tide prediction data

Get tide prediction


## Examples

Get tides for zipcode 98101 from 2023-09-01 to 2023-12-31, looking for low tides less than or equals to +2.5ft, with time range of day between 10:00 and 17:00 on Saturdays(6) and Sundays(7)
```
$ python3 tidechaser.py 20230901 20231231 -z 98101 -s 10:00 -e 17:00 -d 67 -t 2.5

Evaluating with params:
        begin_date:     20230901
        end_date:       20231231
        zipcode:        98101
        start_time:     10:00
        end_time:       17:00
        low_tide:       2.5
        weekdays:       67


Using data from station [9447130] "SEATTLE (Madison St.), Elliott Bay" for 98101:

Time                    Tide(ft)
=================================
2023-09-02 13:09        0.517
2023-09-03 13:55        2.224
2023-09-16 12:21        2.126
2023-09-30 12:04        1.953

```


