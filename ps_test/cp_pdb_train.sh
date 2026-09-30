#!/bin/bash

# Numero di file elencati nella lista
n_files=$(wc -l < name_tot)

for ((b=1; b<=n_files; b++))
do
    # Prendi il nome della directory alla riga `b` nella lista
    subdir=$(sed -n -e "${b}p" < name_tot)

    cd $subdir/"$subdir"_protomer_1


	    for ((f=1; f<=100; f++))
	    do
             if [[ -f  ""$subdir"_stereo_1_vac_md_"${f}".pdb" ]]; then


             mv "$subdir"_stereo_1_vac_md_"${f}".pdb "$subdir"_protomer_1.pdb


       fi
    done
    cd ../..
done

exit

