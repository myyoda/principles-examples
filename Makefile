.POSIX:

all: total.txt

total.txt: prices.csv sum-prices.sh
	./sum-prices.sh

clean:
	rm -f total.txt

.PHONY: all clean
