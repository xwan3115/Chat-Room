import time
import datetime as dt
date = {}
date["Future"] = dt.datetime.now() + dt.timedelta(seconds = 10)
if date["Future"] <= dt.datetime.now():
    print("Succ\n")