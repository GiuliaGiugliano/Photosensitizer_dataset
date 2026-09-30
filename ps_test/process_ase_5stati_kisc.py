#!/usr/bin/env python3
import os
import json
import numpy as np
import pandas as pd
import ase.io

def convert_info_dict(info_dict):
    new_info = {}
    for k, v in info_dict.items():
        if isinstance(v, np.ndarray):
            if v.ndim == 1:
                new_info[k] = ' '.join(f"{x:.25f}" for x in v.tolist())
            else:
                rows = [[float(f"{x:.25f}") for x in row] for row in v.tolist()]
                new_info[k] = '_JSON ' + json.dumps(rows)
        elif isinstance(v, (float, int)):
            new_info[k] = f"{float(v):.25f}"
        else:
            new_info[k] = str(v)
    return new_info

def extract_kisc_vector_t1(ics_path):
    """Estrai 5 valori kISC per T=1, S=1..5 da ics_cost.txt"""
    df = pd.read_csv(ics_path, sep=r'\s+', header=0, engine='python', on_bad_lines='skip')
    df_filt = df[(df['T'] == 1) & (df['S'].between(1, 5))]
    if df_filt.shape[0] != 5:
        raise ValueError(f"Attesi 5 kISC, trovati {df_filt.shape[0]}")
    return df_filt['kisc'].to_numpy(dtype=float).reshape(1, -1)

def first5(df, sufx):
    return df[df['end_state'].str.endswith(sufx)].head(5)

def process_dir(subdir, db):
    try:
        paths = {
            'energy':   "energy_s0_opt.txt",
            'spectrum': "spectrum_col.txt",
            's0_dip':   "s0_dipole_components.txt",
            'charge':   "total_charge.txt",
            'hlgap':    "homo_lumo_gap_col.txt",
            'ics':      "ics_cost.txt",
            'xyz':      "xtbopt.xyz"
        }
        for k, fname in paths.items():
            paths[k] = os.path.join(subdir, fname)

        s0_energy = float(open(paths['energy']).read().strip())
        spec_df = pd.read_csv(paths['spectrum'], delim_whitespace=True, engine='python')
        sing5, trip5 = first5(spec_df, '-1A'), first5(spec_df, '-3A')
        spec10 = pd.concat([sing5, trip5], ignore_index=True)

        ref_energy = np.concatenate(
            ([s0_energy], spec10['Excited_state_energy(eV)'].to_numpy())
        ).reshape(1, -1)

        s0_vec = pd.read_csv(paths['s0_dip'], delim_whitespace=True,
                             header=None).iloc[0, [4, 5, 6]].to_numpy(dtype=float)
        mod_s0 = float(np.linalg.norm(s0_vec))
        mods_exc = spec10['Transition_dipole_module'].to_numpy(dtype=float)
        ref_dipoles = np.concatenate(([mod_s0], mods_exc)).reshape(1, -1)

        ref_wavelen = spec10['excitation_energy(eV)'].to_numpy().reshape(1, -1)
        ref_osc = spec10['fosc'].to_numpy().reshape(1, -1)

        total_charge = float(open(paths['charge']).read().strip())
        hl = pd.read_csv(paths['hlgap'], delim_whitespace=True, header=None).iloc[2, 2]
        ref_hlgap = np.array([[hl, hl]], dtype=float)

        ref_kisc = extract_kisc_vector_t1(paths['ics'])

        mol = ase.io.read(paths['xyz'])
        n_atoms = len(mol)
        ref_scalar = np.full((n_atoms, 1), total_charge, dtype=float)

        mol.info = {
            "REF_energy":     ref_energy,
            "REF_wavelen":    ref_wavelen,
            "REF_oscillator": ref_osc,
            "REF_dipoles":    ref_dipoles,
            "REF_scalar":     ref_scalar,
            "REF_hlgap":      ref_hlgap,
            "REF_kisc":       ref_kisc,
        }

        db.append(mol)
        print(f"✅ Completato: {subdir}")

    except Exception as e:
        print(f"❌ Errore in {subdir}: {e}")

def main():
    list_file = "list_tot"
    if not os.path.isfile(list_file):
        print(f"File {list_file} non trovato.")
        return

    with open(list_file) as f:
        folders = [ln.strip() for ln in f if ln.strip()]

    db = []
    for fold in folders:
        for i in range(1, 21):
            subdir = os.path.join(fold, f"{fold}_protomer_{i}")
            if os.path.isdir(subdir):
                print(f"[FULL SYSTEM] Processing {subdir}")
                process_dir(subdir, db)

    if not db:
        print("Nessuna molecola processata.")
        return

    out_xyz = "full_system_ps_5stati_kisc.xyz"
    with open(out_xyz, "w") as fh:
        for mol in db:
            mol.info = convert_info_dict(mol.info)
            ase.io.write(fh, mol, format='extxyz')
    print(f"✔️ Salvato {out_xyz} ({len(db)} molecole).")

if __name__ == "__main__":
    main()
