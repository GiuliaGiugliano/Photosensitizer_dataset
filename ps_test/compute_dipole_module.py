import json
import numpy as np
from ase import io

def compute_moduli_from_xyz(input_xyz: str, output_xyz: str):
    """
    Legge un file extxyz contenente molte molecole con la proprietà REF_dipoles
    come array di vettori (triplette) o stringa con prefisso _JSON,
    calcola il modulo di ciascun vettore, e salva un nuovo file extxyz
    con REF_dipoles come array di moduli.
    """
    # Lettura molecole
    try:
        mols = io.read(input_xyz, index=':')
    except Exception as e:
        print(f"Errore nella lettura di {input_xyz}: {e}")
        return
    processed = []
    for mol in mols:
        info = mol.info.copy()
        raw = info.get('REF_dipoles')
        if raw is None:
            processed.append(mol)
            continue
        # Se raw è già numpy array
        if isinstance(raw, np.ndarray):
            triplets = raw
        else:
            # raw è stringa, rimuovi prefisso _JSON
            data_str = str(raw).strip()
            if data_str.startswith('_JSON'):
                data_str = data_str[len('_JSON'):].strip()
            # Rimuovi virgolette esterne
            if data_str.startswith('"') and data_str.endswith('"'):
                data_str = data_str[1:-1]
            # Verifica presenza di array esterno
            if not data_str.lstrip().startswith('[['):
                inner = data_str
                if inner.startswith('[') and inner.endswith(']'):
                    inner = inner[1:-1]
                data_str = '[[' + inner + ']]'
            # Parsing JSON
            try:
                triplets = np.array(json.loads(data_str), dtype=float)
            except Exception as e:
                print(f"Errore parsing JSON REF_dipoles per {mol}: {e}")
                processed.append(mol)
                continue
        # Calcolo moduli
        try:
            # triplets shape dovrebbe essere (n,3)
            mods = np.linalg.norm(triplets, axis=1)
        except Exception as e:
            print(f"Errore calcolo moduli per {mol}: {e}")
            processed.append(mol)
            continue
        # Serializza moduli
        mods_list = [float(format(v, '.25f')) for v in mods]
        info['REF_dipoles'] = '_JSON ' + json.dumps(mods_list)
        mol.info = info
        processed.append(mol)
    # Scrittura output
    try:
        with open(output_xyz, 'w') as f:
            for mol in processed:
                io.write(f, mol, format='extxyz')
        print(f"Write completed: {output_xyz}")
    except Exception as e:
        print(f"Errore scrittura di {output_xyz}: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert REF_dipoles triplets to moduli')
    parser.add_argument('input_xyz', help='Path to input extxyz file')
    parser.add_argument('output_xyz', help='Path to output extxyz file')
    args = parser.parse_args()
    compute_moduli_from_xyz(args.input_xyz, args.output_xyz)

