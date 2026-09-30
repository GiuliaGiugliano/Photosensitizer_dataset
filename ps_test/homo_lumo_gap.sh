#!/bin/bash

# Legge ogni riga dalla lista
while read cartella; do
    for i in $(seq 1 20); do
        dir="${cartella}/${cartella}_protomer_${i}"
        if [ -d "$dir" ]; then
            echo "Processing $dir"

            cd "$dir" || continue

            # Estrai il blocco 'ORBITAL ENERGIES' fino alla riga 'Only the first 10 virtual orbitals were printed'
            orbital_energies=$(awk '/ORBITAL ENERGIES/{flag=1} /Only the first 10 virtual orbitals were printed/{flag=0} flag' orca_tddft.log)

            # Estrai le righe con i dati delle energie orbitali (ignorando la riga di intestazione)
            orbital_data=$(echo "$orbital_energies" | grep -E "^[[:space:]]*[0-9]+")

            # Inizializza variabili per il calcolo dell'HOMO-LUMO gap
            homo_energy=0
            lumo_energy=0

            # Trova la riga con occupazione 0.000 (LUMO)
            lumo_line=$(echo "$orbital_data" | awk '$2 == 0.0000 {print $4, $1}' | head -n 1)
            if [ -n "$lumo_line" ]; then
                lumo_energy=$(echo $lumo_line | awk '{print $1}')
            else
                echo "LUMO not found!"
                continue
            fi

            # Trova l'ultima riga con occupazione 2.0000 (HOMO)
            homo_line=$(echo "$orbital_data" | awk '$2 == 2.0000 {print $4, $1}' | tail -n 1)
            if [ -n "$homo_line" ]; then
                homo_energy=$(echo $homo_line | awk '{print $1}')
            else
                echo "HOMO not found!"
                continue
            fi

            # Calcola il gap HOMO-LUMO usando awk
            gap=$(echo "$lumo_energy $homo_energy" | awk '{print $1 - $2}')

            # Stampa i risultati nel terminale
            echo "HOMO energy: $homo_energy eV"
            echo "LUMO energy: $lumo_energy eV"
            echo "HOMO-LUMO gap: $gap eV"

            # Salva il risultato in un file 'homo_lumo_gap.txt' nella stessa sottocartella
            echo -e "HOMO energy: $homo_energy eV\nLUMO energy: $lumo_energy eV\nHOMO-LUMO gap: $gap eV" > homo_lumo_gap.txt
            column -t homo_lumo_gap.txt > homo_lumo_gap_col.txt
            cd - > /dev/null || exit
        fi
    done
done < list_tot

