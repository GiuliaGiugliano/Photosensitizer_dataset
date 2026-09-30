#!/bin/bash

# Numero di file elencati nella lista
n_files=$(wc -l < list_tot)

for ((b=1; b<=n_files; b++))
do
    # Prendi il nome della directory alla riga `b` nella lista
    subdir=$(sed -n -e "${b}p" < list_tot)

cp orca_single_point.slurm $subdir/"$subdir"_protomer_1

done

exit

