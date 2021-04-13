import csv

from alfi import get_default_parser, get_solver
from firedrake import *
from mmsldc2d.mmsldc2d import TwoDimLidDrivenCavityMMSProblem
from mmsldc3d.mmsldc3d import ThreeDimLidDrivenCavityMMSProblem
from pathlib import Path
from pprint import pformat
from time import time


class ResultsCSV(object):
    fields = ['baseN', 'nref', 'degree', 'solver name', 're',
              'velocity', 'velocitygrad', 'pressure', 'divergence',
              'relvelocity', 'relvelocitygrad', 'relpressure',
              'dofs', 'dofs_core', 'runtime',
              'non-linear its', 'total linear its']

    def __init__(self, args, comm=COMM_WORLD):
        self.args = args
        self.comm = comm
        results = Path(self.args.resultsdir)
        csvfilename = str(comm.size) + '_results'
        csvfilename += '_baseN' + str(self.args.baseN)
        csvfilename += '_nref' + str(self.args.nref)
        csvfilename += '.csv'
        self.filepath = results/csvfilename
        if self.comm.rank == 0:
            with open(self.filepath, 'w') as csvf:
                writer = csv.DictWriter(csvf, fieldnames=self.fields)
                writer.writeheader()

    def record_result(self, single_result):
        if self.comm.rank == 0:
            with open(self.filepath, 'a') as csvf:
                writer = csv.DictWriter(csvf, fieldnames=self.fields)
                writer.writerow(single_result)
                csvf.flush()


parser = get_default_parser()
parser.add_argument('--dim', type=int, required=True,
                    choices=[2, 3])
parser.add_argument('--resultsdir',
                    type=str,
                    default='results',
                    help='directory to save results in')
args, _ = parser.parse_known_args()

# Select dimension for problem
if args.dim == 2:
    problem = TwoDimLidDrivenCavityMMSProblem(args.baseN)
elif args.dim == 3:
    problem = ThreeDimLidDrivenCavityMMSProblem(args.baseN)
else:
    raise NotImplementedError

# Create results directory and CSV file
results = Path(args.resultsdir)
if (not results.is_dir()) and (COMM_WORLD.rank == 0):
    try:
        results.mkdir()
    except FileExistsError:
        print('File', cwd,
              'already exists, cannot create directory with the same name')
csvfile = ResultsCSV(args, firedrake.COMM_WORLD)

# Reynolds numbers for continuation
res = [1, 9, 10, 50, 90, 100, 400, 500, 900, 1000]

baseN = args.baseN
nref = args.nref

# Get solver
solver = get_solver(args, problem)
mesh = solver.mesh
h = Function(FunctionSpace(mesh, 'DG', 0)).interpolate(CellSize(mesh))
hs = []
with h.dat.vec_ro as w:
    hs.append((w.max()[1], w.sum()/w.getSize()))
comm = mesh.comm

# Dump solver options and number of DOFs to file
parameters = solver.get_parameters()
dofs = solver.z.function_space().dim()
if comm.rank == 0:
    with open(results/f'{COMM_WORLD.size}_SOLVER_OPTS.txt', 'w') as fh:
        fh.write(pformat(parameters)+'\n')
    with open(results/f'{COMM_WORLD.size}_DOFS.txt', 'w') as fh:
        fh.write(str(dofs)+'\n')

# Results that don't change over continuation
result_dict = {}
result_dict['baseN'] = baseN
result_dict['nref'] = nref
result_dict['degree'] = args.k
result_dict['solver name'] = 'Unknown'
result_dict['dofs'] = dofs
result_dict['dofs_core'] = dofs/comm.size

runtime = 0

# Perform continuation over Reynolds numbers
for re in res:
    problem.Re.assign(re)

    tstart = time()
    (z, info_dict) = solver.solve(re)
    tend = time()
    runtime += tend - tstart

    z = solver.z
    u, p = z.split()
    Z = z.function_space()

    # uviz = solver.visprolong(u)
    # (u_, p_) = problem.actual_solution(uviz.function_space())
    # File('output/u-re-%i-nref-%i.pvd' % (re, nref)).write(uviz.interpolate(uviz))
    # File('output/uerr-re-%i-nref-%i.pvd' % (re, nref)).write(uviz.interpolate(uviz-u_))
    # File('output/uex-re-%i-nref-%i.pvd' % (re, nref)).write(uviz.interpolate(u_))
    (u_, p_) = problem.actual_solution(Z)
    # File('output/perr-re-%i-nref-%i.pvd' % (re, nref)).write(Function(Z.sub(1)).interpolate(p-p_))
    veldiv = norm(div(u))
    pressureintegral = assemble(p_ * dx)
    uerr = norm(u_-u)
    ugraderr = norm(grad(u_-u))
    perr = norm(p_-p)
    pinterp = p.copy(deepcopy=True).interpolate(p_)
    pinterperror = errornorm(p_, pinterp)
    pintegral = assemble(p*dx)

    # Construct a dictionary of output results for each Reynolds number
    single_result = result_dict.copy()
    single_result['re'] = re
    single_result['velocity'] = uerr
    single_result['velocitygrad'] = ugraderr
    single_result['pressure'] = perr
    single_result['relvelocity'] = uerr/norm(u_)
    single_result['relvelocitygrad'] = ugraderr/norm(grad(u_))
    single_result['relpressure'] = perr/norm(p_)
    single_result['divergence'] = veldiv
    single_result['runtime'] = runtime
    single_result['non-linear its'] = info_dict['nonlinear_iter']
    single_result['total linear its'] = info_dict['linear_iter']
    csvfile.record_result(single_result)

    if comm.rank == 0:
        # Investigate different timers
        # ~ from firedrake.petsc import PETSc
        # ~ sneslog = PETSc.Log.Event("SNESSolve").getPerfInfo()
        # ~ print('Python Solve Time Outer:', tend - tstart,
              # ~ 'Python Solve Time Inner:', info_dict['time']*60,
              # ~ 'PETSc Solve Time:', sneslog['time'])
        print('nref', nref, 're', re, ':')
        print('|div(u_h)| = ', veldiv)
        print('p_exact * dx = ', pressureintegral)
        print('p_approx * dx = ', pintegral)
