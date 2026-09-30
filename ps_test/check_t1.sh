#!/bin/bash

LIST="list_tot"
OUTFILE="risultati_orcai_ps.txt"

BASE_DIR="$(pwd -P)"

> "$OUTFILE"

while read -r folder; do
    for subdir in "$BASE_DIR/$folder"/"${folder}"_protomer_*; do

        [[ ! -d "$subdir" ]] && continue

        logfile="$subdir/opt_t1.log"

        if [[ ! -f "$logfile" ]]; then
            echo "$subdir NO" >> "$OUTFILE"
            continue
        fi

        # ORCA deve essere terminato normalmente
        if ! grep -q "ORCA TERMINATED NORMALLY" "$logfile"; then
            echo "$subdir NO" >> "$OUTFILE"
            continue
        fi

        # Caso 1: convergenza esplicita
        if grep -q "\*\*\* *THE OPTIMIZATION HAS CONVERGED *\*\*\*" "$logfile"; then
            echo "$subdir YES" >> "$OUTFILE"
            continue
        fi

        # Caso 2: ultima tabella Geometry convergence
        last_block=$(awk '
            /Geometry convergence/ {flag=1; block=""}
            flag {block = block $0 "\n"}
            /[.]{10,}/ && flag {flag=0}
            END {print block}
        ' "$logfile")

        yes_count=$(echo "$last_block" | awk '{print $NF}' | grep -c "^YES$")

        if [[ "$yes_count" -ge 3 ]]; then
            echo "$subdir YES" >> "$OUTFILE"
        else
            echo "$subdir NO" >> "$OUTFILE"
        fi

    done
done < "$LIST"

