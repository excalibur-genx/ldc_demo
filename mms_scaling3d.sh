#!/bin/bash
## 3D mmsldc strong scaling script

# Run parameters
BATCH_NAME=mms3d_test
RESULTS_DIR=results/${BATCH_NAME}
mkdir -p ${RESULTS_DIR}

# Simulation parameters
BASEN=16
NREF=3
SPACING=1

# Strong scaling
for NODES in 1 2 4 8 16
    do
    if [ $NODES -eq 1 ]
        then
        SPECIAL=":mem=500gb"
    else
        unset SPECIAL
    fi
    qsub -l select=${NODES}${SPECIAL} \
        -N ${BATCH_NAME} \
        -o ${RESULTS_DIR}/${NODES}_nodes.out \
        -e ${RESULTS_DIR}/${NODES}_nodes.err \
        -v NODES=${NODES},SPACING=${SPACING},BASEN=${BASEN},NREF=${NREF} \
        mms3d.pbs
done
