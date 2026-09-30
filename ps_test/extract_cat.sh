#!/usr/bin/env bash
# ------------------------------------------------------------------
# Estrae l’energia del radical-catione (opt_cat.log → energy_cat.txt)
# e, se presenti anche i dati T1, calcola |E_cat – E_T1| → delta_cat_t1.txt
# ------------------------------------------------------------------

LIST="list_tot"   # file con l’elenco delle cartelle base
FAILED_DIRS=()                   # colleziona directory con problemi

while read -r cartella; do
  # scorre i protomeri 1-20
  for i in $(seq 1 20); do
    dir="${cartella}/${cartella}_protomer_${i}"
    [[ -d $dir ]] || continue
    cd "$dir" || { FAILED_DIRS+=("$dir"); continue; }

    # -------- energia del radical-catione (opt_cat.log) ----------
    if [[ -f opt_cat.log ]] && grep -q "ORCA TERMINATED NORMALLY" opt_cat.log; then
      # prende l’ultima “FINAL SINGLE POINT ENERGY”
      e_ha=$(grep "FINAL SINGLE POINT ENERGY" opt_cat.log | tail -n 1 | awk '{print $NF}')
      if [[ -n $e_ha ]]; then
        # converte in eV (1 Ha = 27.211386 eV) e salva
        awk -v v="$e_ha" 'BEGIN{printf "%.10f\n", v*27.211386}' > energy_cat.txt
      fi
    else
      FAILED_DIRS+=("$dir")      # log mancante o terminazione anomala
    fi

    # -------- differenza |E_cat − E_T1| se entrambi i file esistono ----------
    if [[ -s energy_cat.txt && -s energy_t1_opt.txt ]]; then
      e_cat=$(awk 'NR==1{print $1}' energy_cat.txt)
      e_t1=$(awk 'NR==1{print $1}' energy_t1_opt.txt)
      awk -v a="$e_cat" -v b="$e_t1" 'BEGIN{d=a-b; if(d<0)d=-d; print d}' > delta_cat_t1.txt
    fi

    cd - >/dev/null || exit
  done
done < "$LIST"

# ---------- report cartelle problematiche ----------
if ((${#FAILED_DIRS[@]})); then
  printf 'Cartella non valida (opt_cat.log assente o non terminato normalmente):\n'
  printf '%s\n' "${FAILED_DIRS[@]}"
fi
