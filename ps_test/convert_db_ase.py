import os
import numpy as np
import pandas as pd
import ase.io
from ase import Atoms

# Definisci la lista db per salvare le molecole
db = []

def process_dir(subdir):
    try:
        # Carica le energie da energy_s0_opt.txt
        with open(os.path.join(subdir, "energy_s0_opt.txt"), 'r') as f:
            s0_energy = float(f.readline().strip())

        # Carica il dipolo da dipole_s0.txt
        with open(os.path.join(subdir, "dipole_s0.txt"), 'r') as f:
            dipole_s0 = float(f.readline().strip())  # modulo del dipolo S0

        # Carica il file spectrum_col.txt con pandas
        spectrum_df = pd.read_csv(os.path.join(subdir, "spectrum_col.txt"), delim_whitespace=True)

        # Estrai le colonne necessarie dal DataFrame
        excited_energies = spectrum_df['Excited_state_energy(eV)'].to_numpy()[:20]
        wavelengths = spectrum_df['wavelength(nm)'].to_numpy()[:20]
        fosc = spectrum_df['fosc'].to_numpy()[:20]
        transition_dipoles = spectrum_df['Transition_dipole_module'].to_numpy()[:20]

        # REF_energies: [S0] + [E1...E20] + [λ1...λ20] senza i fosc
        ref_energies = np.concatenate((
            [s0_energy],  # energia di S0
            excited_energies,
            wavelengths
        ))

        # Aggiungi il valore HOMO-LUMO gap dal file homo_lumo_gap_col.txt come ultimo elemento in REF_energies
        homo_lumo_file = os.path.join(subdir, "homo_lumo_gap_col.txt")
        homo_lumo_gap = None

        # Leggi il file e prendi il valore dalla riga 3, colonna 3 (indice 2, 2)
        try:
            homo_lumo_df = pd.read_csv(homo_lumo_file, delim_whitespace=True, header=None)
            homo_lumo_gap = homo_lumo_df.iloc[2, 2]  # Terza riga, terza colonna (indice 2)
        except Exception as e:
            print(f"Errore nella lettura di {homo_lumo_file}: {e}")

        # Se il valore è stato trovato, aggiungilo a REF_energies
        if homo_lumo_gap is not None:
            ref_energies = np.append(ref_energies, homo_lumo_gap)

        # REF_dipoles: [dip_s0] + [transition_dipoles]
        ref_dipoles = np.concatenate((
            [dipole_s0],  # modulo dipolo di S0
            transition_dipoles  # moduli dei dipoli di transizione
        ))

        # REF_oscillator: [fosc1...fosc20]
        ref_oscillator = fosc

        # Carica il file con le informazioni di geometria
        xtbopt_file = os.path.join(subdir, "xtbopt.xyz")
        mol = ase.io.read(xtbopt_file, index=0)  # Legge la geometria

        # Carica la carica totale dal file total_charge.txt
        with open(os.path.join(subdir, "total_charge.txt"), 'r') as f:
            total_charge = float(f.readline().strip())

        # REF_charge
        ref_charge = np.array([total_charge])

        # Carica il file soc_calc.txt per i valori SOC
        soc_file = os.path.join(subdir, "soc_calc.txt")
        soc_data = np.loadtxt(soc_file)  # Colonna 3 contiene i valori SOC

        # REF_socs
        ref_socs = soc_data[:, 2]

        # Salva tutte le informazioni nella molecola ASE
        mol.info = {
            "REF_energies": ref_energies,
            "REF_dipoles": ref_dipoles,
            "REF_oscillator": ref_oscillator,  # Aggiungi il nuovo array REF_oscillator
            "REF_socs": ref_socs,
            "REF_scalar": ref_charge
        }

        # Aggiungi la molecola al database
        db.append(mol)

    except Exception as e:
        print(f"Errore in {subdir}: {e}")
        print("Nessuna struttura valida trovata.")

def main():
    with open("list_ps_completi_nodopp") as f:
        cartelle = [line.strip() for line in f if line.strip()]

    for cartella in cartelle:
        for i in range(1, 21):
            subdir = os.path.join(cartella, f"{cartella}_protomer_{i}")
            if os.path.isdir(subdir):
                print(f"Processing {subdir}")
                process_dir(subdir)

    # Aggiungi un controllo prima di scrivere il file .xyz
    if db:
        print(f"Saving {len(db)} structures to full_system.xyz")
        ase.io.write("full_system.xyz", db)
    else:
        print("No valid structures found to save.")

if __name__ == "__main__":
    main()

