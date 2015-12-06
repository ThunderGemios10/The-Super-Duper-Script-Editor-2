CFLAGS=-std=c99 -pedantic -Wall -O2
CC=gcc

all: cpk_uncompress.o
	g++ -shared -Wl,--out-implib,cpk_uncompress.a -o cpk_uncompress.dll cpk_uncompress.o

cpk_uncompress.o: cpk_uncompress.c cpk_uncompress.h

cpk_uncompress: cpk_uncompress.o

clean:
	rm -f cpk_uncompress.a cpk_uncompress.o cpk_uncompress.so cpk_uncompress.dll