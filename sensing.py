import pydht22
import time
from datetime import datetime, timedelta
import urllib.request


baseUrl = "http://api.thingspeak.com/update?api_key={}&field1={:.1f}&field2={:.1f}"
sensors = {
    # GPIO pin: (channel_id, api_key)
    4: ("1234567", "ABCD123"),
#    17: ("1234568", "ABCD123")
}


def get_next_even_minute(minutes):
    now = datetime.now()
    minute = (now.minute // minutes) * minutes + minutes
    if minute >= 60:
        now += timedelta(hours=1)
        minute -= 60
    return now.replace(minute=minute, second=0, microsecond=0)

def sleep_until_next_even_minute(minutes):
    t = get_next_even_minute(minutes)
    while (datetime.now() < t):
        time.sleep(10)

def main():
    while True:
        sleep_until_next_even_minute(10)
        print(datetime.now())
        pins = sensors.keys()
        readings = pydht22.read_sensors(pins)
        for k, v in readings.items():
            channelId = sensors[k][0]
            apiKey = sensors[k][1]
            temp = v[0]
            humidity = v[1]
            print("{}: Temp: {:.1f} C    Humidity: {:.1f} % ".format(k, temp, humidity))
            url = baseUrl.format(apiKey, temp, humidity)
            print(url)
            f = urllib.request.urlopen(url)
            print(f.read())
            f.close()

if __name__ == "__main__":
    main()
