#!/usr/bin/env bash
# divide list_tot in 20 file photo_aa.txt … photo_at.txt

LIST=list_tot                 # file da spezzare
NUM=22                        # parti desiderate

# split con suffisso alfabetico di 2 lettere e aggiunta .txt
split -n l/$NUM --suffix-length=2 --additional-suffix=.txt "$LIST" photo_

echo "Creati $(ls photo_*.txt | wc -l) file: photo_aa.txt …"
