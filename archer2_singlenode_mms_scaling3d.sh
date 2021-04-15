#!/bin/bash
## 3D mmsldc strong scaling script (single node)

# Run parameters
BATCH_NAME=mms3d_singlenode_telescope_6sv3
RESULTS_DIR=results/${BATCH_NAME}
mkdir -p ${RESULTS_DIR}

# Simulation parameters
NODES=1
BASEN=6
NREF=1

# Strong scaling
for NCPU in 1 2 4 8 16 32 64 128
    do
    sbatch -N ${NODES} \
        -J ${BATCH_NAME} \
        -o ${RESULTS_DIR}/${NODES}_nodes_${NCPU}.out \
        -e ${RESULTS_DIR}/${NODES}_nodes_${NCPU}.err \
        --export=NCPU=${NCPU},RESULTS_DIR=${RESULTS_DIR},BASEN=${BASEN},NREF=${NREF} \
        single_mms3d_ho.slm
done
