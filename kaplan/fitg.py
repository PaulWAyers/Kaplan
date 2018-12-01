
from math import factorial
from kaplan.energy import run_energy_calc, prep_psi4_geom
from kaplan.rmsd import calc_rmsd

def get_fitness(xyz_coords, method, basis, fit_form, coef_energy, coef_rmsd, charge, multip):
    return calc_fitness(fit_form, sum_energies(xyz_coords, charge, multip, method, basis), coef_energy, sum_rmsds(xyz_coords), coef_rmsd)

def sum_energies(xyz_coords, charge, multip, method, basis):
    energies = np.zeros(len(xyz_files), float)
    for i, xyz_file in enumerate(xyz_files):
        energies[i] = run_energy_calc(prep_psi4_geom(xyz_file, charge, multip), method, basis)
    return abs(sum(energies))

def sum_rmsds(xyz_coords):
    rmsd_values = np.zeros(len(xyz_files), float)
    # n choose k = n!/(k!(n-k)!)
    num_pairs = factorial(num_geoms)/(2*factorial(num_geoms-2))
    pairs = all_pairs_gen(len(xyz_files))
    for i in range(num_pairs):
        ind1, ind2 = next(pairs)
        rmsd_values[i] = calc_rmsd(xyz_files[ind1], xyz_files[ind2])
    return sum(rmsd_values)

def all_pairs_gen(num_geoms):
    """Yield indices of two geometries.

    Note
    ----
    This is a generator function.

    """
    for i in range(num_geoms-1):
        for j in range(i+1, num_geoms):
            yield (i,j)


def calc_fitness(fit_form, sum_energy, coef_energy, sum_rmsd, coef_rmsd):
    if fit_form == 0:
        return sum_energy*coef_energy + sum_rmsd*coef_rmsd
    else:
        raise ValueError("Unsupported fitness formula.")

#def calc_energy(parser):
#    # TODO: add parser attribute prog
#    # so we can do this:
#    # if parser.prog != 'psi4': blah blah
#    if parser.prog != 'psi4':
#        raise NotImplementedError("Only psi4 is supported at this time.")
#    input_geom = prep_psi4_geom(parser.coords, parser.charge, parser.multip)
#    run_energy_calc(input_geom, parser.method, parser.basis)

#def all_pairs(num_geoms):
#    """Return indices of two geometries."""
#    # n choose k = n!/(k!(n-k)!)
#    num_pairs = factorial(num_geoms)/(2*factorial(num_geoms-2))
#    pairs = []
#    for i in range(num_geoms-1):
#        for j in range(i+1, num_geoms):
#            pairs.append((i,j))
#    assert len(pairs) == num_pairs
#    return pairs