import pydht22
import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt


broker = ("hass.lan", 1883)
sensors = {
    # GPIO pin: topic
    4: "home/garage",
#    17: "home/bedroom",
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

def publish(client, topic, value):
    rc, _ = client.publish(topic, value, qos=1)
    if rc == 0:
        print(f"{topic}: {value}")
    else:
        print(f"Failed to publish {topic} with error code {rc}")

def main():
    while True:
        sleep_until_next_even_minute(10)
        print(datetime.now())
        client = mqtt.Client()
        client.connect(broker[0], broker[1], 60)
        pins = sensors.keys()
        readings = pydht22.read_sensors(pins)
        for k, v in readings.items():
            topic = sensors[k]
            temp = v[0]
            humidity = v[1]
            print("{}: Temp: {:.1f} C, Humidity: {:.1f} % ".format(k, temp, humidity))
            temp_topic = topic + "/temperature"
            publish(client, temp_topic, temp)
            humid_topic = topic + "/humidity"
            publish(client, humid_topic, humidity)

if __name__ == "__main__":
    main()
