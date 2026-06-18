CC ?= cc
BIN = thing

build:
	$(CC) -O2 -o $(BIN) main.c

test: build
	./run_tests.sh

clean:
	rm -f $(BIN)

.PHONY: build test clean
