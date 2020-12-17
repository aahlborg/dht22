/*
 * Program for reading DHT22 sensors using bcm2835 library.
 */

#include <bcm2835.h>
#include <stdio.h>
#include <string.h>
#include <sched.h>
#include <unistd.h>


// Array length macro
#define ARR_LEN(A) (sizeof(A) / sizeof((A)[0]))

// DHT22 data length
#define DATA_BYTES (5u)
#define DATA_BITS (8u * DATA_BYTES)

// Sensor read status codes
#define E_OK (0)
#define E_TIMEOUT (-1)
#define E_PERIOD (-2)
#define E_CHECKSUM (-3)


struct sensor
{
  int pin;
  char name[20];
};


struct sensor sensors[] = 
{
  {4, "Sensor 1"},
  {17, "Sensor 2"}
};


int getMicros(void)
{
  // Read and truncate system counter value to 32 bits
  return (int)bcm2835_st_read();
}

void set_prio_rt(void)
{
  struct sched_param sched;
  memset(&sched, 0, sizeof(sched));
  sched.sched_priority = sched_get_priority_max(SCHED_FIFO);
  sched_setscheduler(0, SCHED_FIFO, &sched);
}

void set_prio_other(void)
{
  struct sched_param sched;
  memset(&sched, 0, sizeof(sched));
  sched.sched_priority = 0;
  sched_setscheduler(0, SCHED_OTHER, &sched);
}

int read_sensor(int pin, unsigned char data[5])
{
  int bit_times[DATA_BITS];
  int t0, t1;

  // Raise the prio of the thread to RT, if possible
  set_prio_rt();

  // Configure the pin as output
  bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);
  // Set pin low
  bcm2835_gpio_write(pin, LOW);
  // Wait 2 ms
  bcm2835_delay(2);
  // Set pin high
  bcm2835_gpio_write(pin, HIGH);
  // Configure pin as input
  bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);

  // Wait until pin is low
  // Should take 20-40 us
  t0 = getMicros();
  while (bcm2835_gpio_lev(pin) == HIGH)
  {
    t1 = getMicros();
    if (t1 - t0 > 100)
    {
      set_prio_other();
      return E_TIMEOUT;
    }
  }

  // Wait until pin is high
  // Should take 80 us
  t0 = getMicros();
  while (bcm2835_gpio_lev(pin) == LOW)
  {
    t1 = getMicros();
    if (t1 - t0 > 100)
    {
      set_prio_other();
      return E_TIMEOUT;
    }
  }

  // Wait until pin low
  // Should take 80 us
  t0 = getMicros();
  while (bcm2835_gpio_lev(pin) == HIGH)
  {
    t1 = getMicros();
    if (t1 - t0 > 100)
    {
      set_prio_other();
      return E_TIMEOUT;
    }
  }

  // Loop for each bit
  // Break if all 40 bits received or if timeout (100 µs)
  for (int i = 0; i < DATA_BITS; i++)
  {
    // Wait until pin high
    t0 = getMicros();
    while (bcm2835_gpio_lev(pin) == LOW)
    {
      t1 = getMicros();
      if (t1 - t0 > 100)
      {
        set_prio_other();
      return E_TIMEOUT;
      }
    }

    // Wait until pin low
    t0 = getMicros();
    while (bcm2835_gpio_lev(pin) == HIGH)
    {
      t1 = getMicros();
      if (t1 - t0 > 100)
      {
        set_prio_other();
      return E_TIMEOUT;
      }
    }

    // Store high time
    bit_times[i] = t1 - t0;
  }

  // Lower prio of thread to normal
  set_prio_other();

  // Interpret bits and store in 5 byte array
  // * 0 if time is 15-40 µs
  // * 1 if time is 60-90 µs
  // * Else fail
  memset(data, 0, DATA_BYTES);
  for (int i = 0; i < DATA_BITS; i++)
  {
    int byte = i / 8;
    int bit = 7 - (i % 8);
    int val;

    if (bit_times[i] < 15)
    {
      return E_PERIOD;
    }
    else if (bit_times[i] < 40)
    {
      val = 0;
    }
    else if (bit_times[i] < 60)
    {
      return E_PERIOD;
    }
    else if (bit_times[i] < 90)
    {
      val = 1;
    }
    else
    {
      return E_PERIOD;
    }

    data[byte] |= (val << bit);
  }

  // Compute and verify checksum
  unsigned char checksum = data[0] + data[1] + data[2] + data[3];
  if (checksum != data[4])
  {
    return E_CHECKSUM;
  }

  return E_OK;
}

void decode_data(unsigned char data[5], float * temp, float * humid)
{
  short temp_int = (data[2] << 8) | (data[3]);
  *temp = temp_int / 10.0f;
  short humid_int = (data[0] << 8) | (data[1]);
  *humid = humid_int / 10.0f;
}

int process_sensor(struct sensor sensor)
{
  unsigned char data[DATA_BYTES];

  int status = read_sensor(sensor.pin, data);
  if (E_OK == status)
  {
    float temp, humid;
    decode_data(data, &temp, &humid);
    printf("Sensor %s\n", sensor.name);
    printf("Temp: %.1f *C, humidity: %.1f \%RH\n", temp, humid);
  }

  return status;
}

int main(int argc, char** argv)
{
  // Initialize IO
  if (!bcm2835_init())
    return 1;
  
  for (int i = 0; i < ARR_LEN(sensors); i++)
  {
    for (int j = 0; j < 5; j++)
    {
      if (E_OK == process_sensor(sensors[i]))
        break;
      // Wait 2 seconds for next attempt
      sleep(2);
    }
  }
 
  bcm2835_close();
}
