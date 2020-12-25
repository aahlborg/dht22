SOURCES := dht22.c
LIBS := -lbcm2835
CCFLAGS := -O2

all: dht22 dht22.so

clean:
	rm -f dht22 dht22.so

dht22: $(SOURCES)
	gcc -o dht22 $(CCFLAGS) $(SOURCES) $(LIBS)

dht22.so: $(SOURCES)
	gcc --shared -o dht22.so $(CCFLAGS) $(SOURCES) $(LIBS)
