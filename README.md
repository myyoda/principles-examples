# Grocery Receipt Analysis (containerized)

Run `make` to produce `total.txt` from `prices.csv`.

The analysis runs inside an Alpine Linux container to guarantee
identical results regardless of the host system's awk version.

Requires: POSIX sh, make, singularity (or apptainer).
The container image (`alpine_3.21.sif`) must be present in the
parent directory — see Makefile for details.
