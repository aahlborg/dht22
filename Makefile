SOURCES := dht22.c
LIBS := -lbcm2835
CCFLAGS := -g

all: dht22

clean:
	rm -f dht22

dht22: $(SOURCES)
	gcc -o dht22 $(CCFLAGS) $(SOURCES) $(LIBS)
