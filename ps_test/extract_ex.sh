#!/bin/bash

# Legge ogni riga dalla lista
while read cartella; do
    for i in $(seq 1 20); do
        dir="${cartella}/${cartella}_protomer_${i}"
        if [ -d "$dir" ]; then
            echo "Processing $dir"

            cd "$dir" || continue

            # 1. Estrai lo spettro

             grep -a -A24 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' orca_tddft.log | head -n 25 | tail -n20 > spectrum.txt
             val=$(awk 'NR==1 {print $1}' energy_s0_opt.txt) && awk -v v="$val" '{print $0, v}' spectrum.txt > tmp && mv tmp spectrum.txt
	     awk '{print $0}' spectrum.txt | sort -k3,3n | awk '
{
    if ($3 ~ /-[1]A$/) {
        print > "singlets.tmp"
    } else if ($3 ~ /-[3]A$/) {
        print > "triplets.tmp"
    }
}
END {
    system("cat singlets.tmp triplets.tmp > spectrum.txt; rm singlets.tmp triplets.tmp")
}
'



awk '{sum = $4 + $12; printf "%s %.13f\n", $0, sum}' spectrum.txt > tmp && mv tmp spectrum.txt

awk 'BEGIN {print "start_state to   end_state  excitation_energy(eV)  excitation_energy(cm-1)  wavelength(nm)  fosc  D2  DX  DY  DZ  S0_min_energy(eV)  Excited_state_energy(eV)  Transition_dipole_module"} 
     {sqrt_col = sqrt($8); printf "%s %.8f\n", $0, sqrt_col}' spectrum.txt | column -t > spectrum_col.txt



            cd - > /dev/null || exit
        fi
    done
done < list_tot

