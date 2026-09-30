#!/usr/bin/env bash
# make_xtb_scripts.sh
# genera run_xtb_aa.sh … run_xtb_av.sh
# ognuno userà la lista photo_aa.txt … photo_av.txt
# autore: ggiugliano – 2025-04-27

XTB_OPTS="--opt vtight --gbsa h2o --uhf 0"   # opzioni comuni (senza --chrg)

for suf in {a..v}; do
    list="photo_a${suf}.txt"
    out="run_xtb_a${suf}.sh"

cat > "$out" <<'EOF'
#!/usr/bin/env bash
LIST="__LIST__"                 # sostituito dal generatore
XTB_OPTS="__XTB_OPTS__"

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
EOF

    # sostituzioni in-place
    sed -i "s|__LIST__|$list|"     "$out"
    sed -i "s|__XTB_OPTS__|$XTB_OPTS|" "$out"

    chmod +x "$out"
    echo "Creato: $out (usa $list)"
done
