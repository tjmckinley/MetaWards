LD = gcc
CC = gcc

GSL_INC = $(shell gsl-config --cflags)
GSL_LIB = $(shell gsl-config --libs)

JSON_C_INC = -I/usr/local/include/json-c    # $(shell pkg-config --cflags json-c)
JSON_C_LIB = -L/usr/local/include -ljson-c  # $(shell pkg-config --libs json-c)

CFLAGS = $(GSL_INC) $(GSL_LIB) $(JSON_C_INC) $(JSON_C_LIB)

metawards: src/*.c src/*.h
	$(CC) src/*.c -o metawards $(CFLAGS) -Isrc -lgsl -lm -O3

clean:  
	rm metawards
