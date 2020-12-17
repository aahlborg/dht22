# Humidity sensing

The Python approach uses adafruit_dht library which polls the wire continously, using 100% CPU per sensor.

Try to use C library bcm2835 to read the DHT22 sensor.


# DHT22 communication

A single pull-up wire is used for two-way communication.

## Initialization

Communication is initialized by the host pulling the line low for at least 1 ms. Then the host releases the line and waits for sensor response. After 20-40 µs the sensor pulls the line low for 80 µs and then releases it for 80 µs.

| Time (µs) | Host | Sensor |
|--|--|--|
| 1000 | Low | - |
| 20-40 | Release | - |
|--|--|--|
| 80 | - | Low |
| 80 | - | High |


## Bit coding

Each bit is transmitted as a 50 µs low signal followed by a variable length high signal. A 0 is coded as a 26-28 µs high signal and a 1 is coded as a 70 µs high signal.

| Time (µs) | Level |
|--|--|
| 50 | Low |
| 27 | High (if 0) |
| 70 | High (if 1) |


## Data format

DHT22 send out the higher data bit first!

    |  8 bit  |   8 bit  |   8 bit   |  8 bit   |   8 bit  |
    | high RH |  low RH  | high temp | low temp | checksum |

| Length | Data |
|--|--|
| 8 bits | RH integral part |
| 8 bits | RH decimal part |
| 8 bits | Temp integral part |
| 8 bits | Temp decimal part |
| 8 bits | Checksum |

The checksum is the last 8 bits of the sum of all data fields.

Humidity is calculated as ((data[0] << 8) | (data[1])) / 10 in % RH.
Temp is calculated as ((data[2] << 8) | (data[3])) / 10 in *C.


## Failure

If reading the sensor fails for some reason the master must wait at least 2 seconds until attempting to read again.


# C approach

Use bcm2835 library to manually poll the sensor only when requesting a reading.

## Building

    gcc -o dht22 dht22.c -lcurl -lbcm2835


## Reading the sensor

Initialization

* Raise the prio of the thread to RT, if possible
* Configure the pin as output
* Set pin low
* Wait 1000 µs
* Set pin high
* Configure pin as input
* Wait until pin is low
* Wait until pin is high
* Expect 50-100 µs of each high end low, else fail
* Wait until pin low

Data collection

* Loop for each bit
  * Wait until pin high
  * Wait until pin low
  * Measure and store high time
  * Break if all 40 bits received or if timeout (100 µs)
* Lower prio of thread to normal

Data interpretation

* Interpret bits and store in 5 byte array
  * 0 if time is 15-50 µs
  * 1 if time is 50-100 µs
  * Else fail
* Compute and verify checksum
* Return data and status code
  * 0: Success
  * -1: Timing error or timeout
  * -2: Checksum error


# References

* https://www.airspayce.com/mikem/bcm2835/
* https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf
* https://github.com/gorskima/dht22-reader
