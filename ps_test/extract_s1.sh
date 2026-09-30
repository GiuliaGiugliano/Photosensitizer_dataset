#!/usr/bin/env bash

LIST="list_tot"
FAILED_DIRS=()

while read -r cartella; do
  for i in $(seq 1 20); do
    dir="${cartella}/${cartella}_protomer_${i}"
    [[ -d $dir ]] || continue
    cd "$dir" || continue

    if [[ -f opt_s1.log ]] && grep -q "ORCA TERMINATED NORMALLY" opt_s1.log; then
      e=$(grep "FINAL SINGLE POINT ENERGY" opt_s1.log | tail -n 1 | awk '{print $NF}')
      [[ -n $e ]] && awk -v v="$e" 'BEGIN { printf "%.10f\n", v*27.211386 }' > energy_s1_opt.txt
    else
      FAILED_DIRS+=("$dir")
    fi

    if [[ -s energy_s1_opt.txt && -s energy_t1_opt.txt ]]; then
      s0=$(awk 'NR==1{print $1}' energy_s1_opt.txt)
      t1=$(awk 'NR==1{print $1}' energy_t1_opt.txt)
      awk -v a="$s0" -v b="$t1" 'BEGIN{d=a-b; if(d<0)d=-d; print d}' > delta_s1_t1.txt
    fi

    cd - >/dev/null || exit
  done
done < "$LIST"

((${#FAILED_DIRS[@]})) && printf 'Cartella non valida: %s\n' "${FAILED_DIRS[@]}"
