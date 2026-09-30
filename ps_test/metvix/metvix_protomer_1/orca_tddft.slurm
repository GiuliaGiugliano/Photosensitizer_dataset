#!/bin/bash 
#SBATCH -t 48:00:00 
#SBATCH -p barnard 
#SBATCH -N 1 
#SBATCH --tasks-per-node=16 
#SBATCH --mem=32G

module load release/24.04
module load GCC/12.3.0
module load OpenMPI/4.1.5
module load ORCA/6.0.1-avx2


/software/rapids/r24.04/ORCA/6.0.1-gompi-2023a-avx2/bin/orca  orca_tddft.inp > orca_tddft.log


rm -f *tmp
