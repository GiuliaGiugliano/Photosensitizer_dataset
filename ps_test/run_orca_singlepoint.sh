#!/bin/bash

# Numero di file elencati nella lista
n_files=$(wc -l < list_tot)

for ((b=1; b<=n_files; b++))
do
    # Prendi il nome della directory alla riga `b` nella lista
    subdir=$(sed -n -e "${b}p" < list_tot)

    # Ciclo sui possibili protomeri da 1 a 20
    for ((i=1; i<=20; i++))
    do
        # Verifica se la sottocartella subdir_protomer_i esiste
        protomer_subdir="$subdir/${subdir}_protomer_${i}"

        if [[ -d "$protomer_subdir" ]]; then
            # Se la sottocartella esiste, entra nella sottocartella
            cd "$protomer_subdir" || exit

            # Copia il file orca.slurm dalla cartella principale alla sottocartella
            if [[ -f "../../orca_single_point.slurm" ]]; then
                cp "../../orca_single_point.slurm" .
            else
                echo "File orca.slurm non trovato nella cartella principale!"
                continue
            fi

            # Lancia lo script sbatch se il file opt_s0_orca.inp esiste nella sottocartella
            if [[ -f opt_s0_orca_singlepoint.inp ]]; then
                sbatch orca_single_point.slurm
            fi

            # Torna alla directory principale
            cd - || exit
        fi
    done
done

exit
