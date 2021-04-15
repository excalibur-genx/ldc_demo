#!/bin/bash
## 3D mmsldc strong scaling script (single node)

# Run parameters
BATCH_NAME=mms3d_small12_4
RESULTS_DIR=results_mms/${BATCH_NAME}
mkdir -p ${RESULTS_DIR}

# Simulation parameters
NODES=1
BASEN=12
NREF=2

# Strong scaling
for NCPU in 1 2 4 8 16 32 64
    do
    if [ $NODES -eq 1 ]
        then
        SPECIAL=":mem=500gb"
    else
        unset SPECIAL
    fi
    qsub -l select=${NODES}${SPECIAL} \
        -N ${BATCH_NAME} \
        -o ${RESULTS_DIR}/${NODES}_nodes_${NCPU}.out \
        -e ${RESULTS_DIR}/${NODES}_nodes_${NCPU}.err \
        -v NCPU=${NCPU},BASEN=${BASEN},NREF=${NREF},RESULTS_DIR=${RESULTS_DIR} \
        mms_scaling/single_mms3d.pbs
done
