#!/usr/bin/env bash
# ------------------------------------------------------------------
# Estrae l’energia del radical-anione (opt_an.log → energy_an.txt)
# e, se presente anche energy_s0_opt.txt, calcola |E_s0 – E_an|
# → delta_s0_an.txt
# ------------------------------------------------------------------

LIST="list_tot"   # file con l’elenco delle cartelle base
FAILED_DIRS=()                   # colleziona directory con problemi

while read -r cartella; do
  # scorre i protomeri 1-20
  for i in $(seq 1 20); do
    dir="${cartella}/${cartella}_protomer_${i}"
    [[ -d $dir ]] || continue
    cd "$dir" || { FAILED_DIRS+=("$dir"); continue; }

    # -------- energia del radical-anione (opt_an.log) ----------
    if [[ -f opt_an.log ]] && grep -q "ORCA TERMINATED NORMALLY" opt_an.log; then
      # prende l’ultima “FINAL SINGLE POINT ENERGY”
      e_ha=$(grep "FINAL SINGLE POINT ENERGY" opt_an.log | tail -n 1 | awk '{print $NF}')
      if [[ -n $e_ha ]]; then
        # converte in eV (1 Ha = 27.211386 eV) e salva
        awk -v v="$e_ha" 'BEGIN{printf "%.10f\n", v*27.211386}' > energy_an.txt
      else
        FAILED_DIRS+=("$dir")  # errore nell'estrazione dell'energia
      fi
    else
      FAILED_DIRS+=("$dir")    # log mancante o terminazione anomala
    fi

    # -------- differenza |E_s0 – E_an| se entrambi i file esistono ----------
    if [[ -s energy_s0_opt.txt && -s energy_an.txt ]]; then
      e_s0=$(awk 'NR==1{print $1}' energy_s0_opt.txt)
      e_an=$(awk 'NR==1{print $1}' energy_an.txt)
      awk -v a="$e_s0" -v b="$e_an" 'BEGIN{d=a-b; if(d<0)d=-d; print d}' > delta_s0_an.txt
    fi

    cd - >/dev/null || exit
  done
done < "$LIST"

# ---------- report cartelle problematiche ----------
if ((${#FAILED_DIRS[@]})); then
  printf 'Cartelle con errori (opt_an.log assente o non terminato normalmente o energia mancante):\n'
  printf '%s\n' "${FAILED_DIRS[@]}"
fi
