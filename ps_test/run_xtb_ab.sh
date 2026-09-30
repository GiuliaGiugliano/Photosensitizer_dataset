#!/usr/bin/env bash
LIST="photo_ab.txt"                 # sostituito dal generatore
XTB_OPTS="--opt vtight --gbsa h2o --uhf 0"

while IFS= read -r folder || [[ -n $folder ]]; do
    [[ -z $folder || $folder =~ ^# ]] && continue   # salta righe vuote o commenti

    workdir="${folder}/${folder}_protomer_1"
    xyzfile="${folder}_protomer_1.xyz"
    chargefile="${workdir}/charge.txt"

    if [[ -d $workdir && -f $workdir/$xyzfile ]]; then
        if [[ -f $chargefile ]]; then
            charge=$(< "$chargefile")
        else
            echo "!!! $folder: charge.txt mancante, uso 0" >&2
            charge=0
        fi

        echo ">>> $workdir  (Q=$charge)"
        (
            cd "$workdir" || exit 1
            xtb "$xyzfile" $XTB_OPTS --chrg "$charge" > xtb.log 2>&1
        )
    else
        echo "!!! Skipped $folder  (dir o .xyz mancante)" >&2
    fi
done < "$LIST"
