.POSIX:
SIF = ../alpine_3.21.sif

all: total.txt

total.txt: prices.csv sum-prices.sh $(SIF)
	singularity exec --cleanenv $(SIF) ./sum-prices.sh

clean:
	rm -f total.txt

.PHONY: all clean
