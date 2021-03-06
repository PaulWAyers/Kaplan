"""This module uses psi4 to run energy calculations
for a given geometry."""

import os
import psi4

# TODO: make these functions callable from a function
# that checks the program being used (i.e. psi4 vs horton
# vs gaussian)

# how much RAM to use for psi4 calculations
# should be less than what your computer has available
RAM = "4 GB"


def run_energy_calc(geom, method="hf", basis="sto-3g",
                    restricted=False):
    """Run an energy calculation using psi4.

    Parameters
    ----------
    geom : str
        The string representing the molecular
        geometry for which to evaluate the energy.
        Note: this string should be generated using
        the prep_psi4_geom() function.

    method : str
        The quantum mechanical method to use.

    basis : str
        The basis set to use for the calculation.

    restricted : bool
        Default is False (runs an unrestricted
        calculation). If set to True, runs a
        restricted calculation.

    Raises
    ------
    AssertionError
        The method, basis, or geom variable
        is not a string.

    Returns
    -------
    A floating point number representing the energy
    of the given molecule, for the given basis set
    and method, in hartrees.

    Notes
    -----
    Restricted might not work for non-hf methods.

    """
    psi4.set_memory(RAM)
    psi4.core.be_quiet()
    assert isinstance(method, str)
    assert isinstance(basis, str)
    if restricted:
        psi4.set_options({"reference": "uhf"})
    try:
        energy = psi4.energy(method+'/'+basis, return_wfn=False)
    except psi4.driver.p4util.exceptions.ValidationError:
        raise psi4.driver.p4util.exceptions.ValidationError(f"Invalid method: {method}")
    except psi4.driver.qcdb.exceptions.BasisSetNotFound:
        raise psi4.driver.qcdb.exceptions.BasisSetNotFound(f"Invalid basis set: {basis}")
    return energy


def check_psi4_inputs(qcm, basis):
    """Check that a method and a basis set are available in psi4.

    Parameters
    ----------
    qcm : str
        The name of the method to use (lowercase).
    basis : str
        The name of the basis set (lowercase).

    Returns
    -------
    bool
        True if calculation can be run with basis
        set and method given. Otherwise raise
        the ValueError.

    Notes
    -----
    For now, this function will do a try accept to
    determine if the calculation is legitimate.
    Later on, this might be changed to reading in
    datafiles containing lists of acceptable inputs
    and comparing those lists to the program input.

    """
    # directory for data files
    avail_basis = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'data/psi4-basis-sets.txt')
    avail_qcm = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'data/psi4-methods.txt')
    geom = psi4.geometry("""
                         0 1
                         H 0.0 0.0 0.0
                         H 0.0 0.0 1.0
                         """)
    try:
        run_energy_calc(geom, qcm, basis)
        return True
    except psi4.driver.p4util.exceptions.ValidationError:
        raise ValueError(f"Invalid method: {qcm}")
    except psi4.driver.qcdb.exceptions.BasisSetNotFound:
        raise ValueError(f"Invalid basis: {basis}")


def prep_psi4_geom(coords, charge, multip):
    """Make a psi4 compliant geometry string.

    Parameters
    ----------
    coords : list(list)
        Atomic cartesian coordinates and atom types.
        Example for H_2:
        [['H', 0.0, 0.0, 0.0], ['H', 0.0, 0.0, 1.0]]
    charge : int
        The charge of the molecule.
    multip : int
        The multiplicity of the molecule.

    Returns
    -------
    A string as per psi4 input.

    """
    psi4_str = f"\n{charge} {multip}\n"
    for atom in coords:
        psi4_str += f"{atom[0]} {atom[1]} {atom[2]} {atom[3]}\n"
    return psi4.geometry(psi4_str)
