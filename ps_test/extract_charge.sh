#!/usr/bin/env bash

INPUT="list_tot"

while IFS= read -r FOLDER; do
    PROT_DIR="${FOLDER}/${FOLDER}_protomer_1"
    INP_FILE="${PROT_DIR}/orca_tddft.inp"
    OUT_FILE="${PROT_DIR}/total_charge.txt"

    if [[ -f "$INP_FILE" ]]; then
        CHARGE=$(grep -E '^\* xyzfile' "$INP_FILE" | awk '{print $3}')
        echo "$CHARGE" > "$OUT_FILE"
    else
        echo "FILE_MANCANTE" > "$OUT_FILE"
    fi
done < "$INPUT"

echo "Estrazione completata." 
