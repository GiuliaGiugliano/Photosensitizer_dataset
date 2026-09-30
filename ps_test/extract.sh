#!/bin/bash

# Legge ogni riga dalla lista
while read cartella; do
    for i in $(seq 1 20); do
        dir="${cartella}/${cartella}_protomer_${i}"
        if [ -d "$dir" ]; then
            echo "Processing $dir"

            cd "$dir" || continue

            # 1. Estrai la carica dal file .smi
            smi_file=$(ls *.smi 2>/dev/null | head -n 1)
            if [[ -f "$smi_file" ]]; then
                charge=$(awk '{print $2}' "$smi_file")
                echo "$charge" > total_charge.txt
            fi

            # 2. Estrai energia e moltiplica per 27.211386
            energy_line=$(grep "FINAL SINGLE POINT ENERGY" opt_s0_orca_single_point.log 2>/dev/null)
            if [[ -n "$energy_line" ]]; then
                raw_energy=$(echo "$energy_line" | awk '{print $NF}')
                energy_ev=$(awk -v e="$raw_energy" 'BEGIN {printf "%.10f", e * 27.211386}')
                echo "$energy_ev" > energy_s0_opt.txt
            fi

            # 3. Calcolo momento di dipolo
            dipole_line=$(grep "Total Dipole Moment" opt_s0_orca_single_point.log 2>/dev/null)

            echo $dipole_line > s0_dipole_components.txt
            cd - > /dev/null || exit
        fi
    done
done < list_tot

