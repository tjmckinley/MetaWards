LD = gcc
CC = gcc

metawards: src/*.c src/*.h
	$(CC) src/*.c -o metawards $(shell gsl-config --cflags) $(shell gsl-config --libs) -Isrc -lgsl -lm -O3

clean:  
	rm metawards
