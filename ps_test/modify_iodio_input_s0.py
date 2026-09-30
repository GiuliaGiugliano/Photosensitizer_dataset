import os

# Percorso del file che contiene i path
file_iodine = "iodine_atom.txt"

# Nuove righe da inserire
new_first_line = "! b3lyp_g zora zora-def2-tzvp RI-SOMF(1X) SARC/J\n"
new_block = """%BASIS
        newgto I  \"sarc-zora-tzvp\" end
end
"""

# Legge il file con i path
with open(file_iodine, "r") as f:
    paths = [line.split()[0] for line in f.readlines()]

# Itera sui path e modifica i file
for path in paths:
    input_file = os.path.join(path, "opt_s0_orca_singlepoint.inp")

    if os.path.exists(input_file):
        with open(input_file, "r") as f:
            lines = f.readlines()

        # Modifica la prima riga
        lines[0] = new_first_line

        # Cerca dove inserire il nuovo blocco prima della riga * xyzfile
        for idx, line in enumerate(lines):
            if line.strip().startswith("* xyzfile"):
                lines.insert(idx, new_block)
                break

        # Scrive il file modificato
        with open(input_file, "w") as f:
            f.writelines(lines)

        print(f"Modificato: {input_file}")
    else:
        print(f"File non trovato: {input_file}")

