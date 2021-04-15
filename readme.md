# LDC Demo

Solves a 2D or 3D Lid Driven Cavity Navier Stokes problem using Firedrake with a variety of solver options.

You will require a working [Firedrake](https://www.firedrakeproject.org) install to run this code, together with [ALFI](https://github.com/florianwechsung/alfi).

The simulation code is in `mms_scaling.py` and the built in help for command line parameters can be seen by running `python mms_scaling.py --help`.

Example usage:

```bash
mpiexec -n 8 python mms_scaling.py \
    --resultsdir results/poisson_patch \
    --dim 3 \
    --baseN 12 \
    --nref 3 \
    --k 1 \
    --discretisation pkp0 \
    --solver-type almg \
    --mh uniform \
    --patch star \
    --gamma 1e4 \
    --stabilisation-type supg \
    --stabilisation-weight 0.05 \
    --telescope_factor 1
```

- `dim` is the numbers of spatial dimensions (2D or 3D)
- `baseN` corresponds to the size of the coarsest grid in the multigrid solver
- `nref` corresponds to the number of multigrid refinements (multigrid levels minus 1)
- `k` is the finite element degree (for the velocity field)
- `discretisation` selects the finite element family
- The remaining options correspond to different solver parameters

Example submission scripts (`.pbs`) for the Isambard UK tier 2 HPC facility and strong scaling submission script is provided for 2D and 3D simulation:
```
mms2d.pbs
mms3d.pbs
mms_scaling2d.sh
mms_scaling3d.sh
single_mms_scaling3d.sh
```

Example submission scripts (`.slm`) for the ARCHER2 UK national HPC facility and strong scaling submission script _for a single node_ is provided for 3D simulation at.
```
single_mms3d.slm
single_mms3d_ho.slm
archer2_singlenode_mms_scaling3d.sh
```
