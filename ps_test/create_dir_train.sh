#!/bin/bash

# Numero di file elencati nella lista
n_files=$(wc -l < list2)

for ((b=1; b<=n_files; b++))
do
    # Prendi il nome della directory alla riga `b` nella lista
    subdir=$(sed -n -e "${b}p" < list2)
    mkdir $subdir
    cd $subdir
    mkdir "$subdir"_protomer_1 
   cd ..  
done

exit

