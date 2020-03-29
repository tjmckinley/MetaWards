LD = gcc
CC = gcc

wards: *.c *.h
	$(CC) *.c -o metawards $(shell gsl-config --cflags) $(shell gsl-config --libs) -lgsl -lm -O3

clean:  
	rm metawards
