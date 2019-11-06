"""This module uses Psi4 and Openbabel to run energy calculations
for a given geometry."""

import os
import sys
import psi4
import pybel
import openbabel

from numpy import allclose

from kaplan.inputs import Inputs, hardware_inputs
from kaplan.geometry import set_coords, get_coords, periodic_table


class BasisSetError(Exception):
    """Raised if basis set cannot be found for a program."""


class MethodError(Exception):
    """Raised if there is an issue whereby the energy cannot be calculated.

    This includes:
    * quantum chemical method is unavailable
    * force field cannot be setup for a molecule
    * forcefield is unavailable

    """


def run_energy_calc(coords):
    """Setup and execute an energy calculation.

    Parameters
    ----------
    coords : np.array(shape=(n,3), dtype=float)
        xyz coordinates for a n-atom conformer.
        Units of atomic units.

    Notes
    -----
    This function uses the hardware_inputs dictionary
    located at the top of the inputs file. Other input
    arguments can be added to the inputs extra
    dictionary (i.e. inputs.extra["myarg"] = "myval").
    If an argument is added to the extra dictionary
    that is in the default arguments, the extra
    dictionary takes precedence. Unless the user
    has changed the code, the extras are unlikely
    to impact the energy calculation.

    Returns
    -------
    Energy result as a floating point number.

    """
    inputs = Inputs()
    # if you added extra options, they are included here
    extras = {}
    for arg, val in inputs.extra.items():
        extras[arg] = val

    defaults = hardware_inputs[inputs.prog]
    for key in defaults:
        if key not in extras:
            extras[key] = defaults[key]
    if inputs.prog == "psi4":
        geom_str = prep_psi4_geom(coords, inputs.atomic_nums, inputs.charge, inputs.multip)
        energy = psi4_energy_calc(geom_str, inputs.method, inputs.basis,
                                  extras["RAM"])
        # energy is in hartrees here
        return energy
    elif inputs.prog == "openbabel":
        # check obmol has current geometry
        if not allclose(coords, get_coords(inputs.obmol)):
            set_coords(inputs.obmol, coords)
        energy = obabel_energy(inputs.method, inputs.obmol)
        return energy
    raise NotImplementedError("Program not found.")


def psi4_energy_calc(geom, method, basis, ram):
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
    ram : str
        Specifies how much memory to use in calculations.
        Should be something like "4 GB".

    Raises
    ------
    BasisSetError
        The basis set did not work using psi4.
    MethodError
        The method did not work using psi4.

    Returns
    -------
    A floating point number representing the energy
    of the given molecule, for the given basis set
    and method, in hartrees.

    """
    psi4.core.be_quiet()
    psi4.set_memory(ram)
    mol = psi4.geometry(geom)
    try:
        energy = psi4.energy(
            f"{method}/{basis}", return_wfn=False, molecule=mol
        )
        psi4.core.clean()
        return energy
    except psi4.driver.p4util.exceptions.ValidationError:
        raise MethodError(f"Invalid method for Psi4: {method}")
    except psi4.driver.qcdb.exceptions.BasisSetNotFound:
        raise BasisSetError(f"Invalid basis set for Psi4: {basis}")


def prep_psi4_geom(coords, atomic_nums, charge, multip):
    """Make a psi4 compliant geometry string.

    Parameters
    ----------
    coords : list(np.array((num_atoms, 3), float)
        Atomic cartesian coordinates and atom types.
        Example for H_2:
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.88]])
    atomic_nums : np.array(num_atoms, dtype=int)
        Atomic numbers of the atoms in the geometry.
    charge : int
        The charge of the molecule.
    multip : int
        The multiplicity of the molecule.

    Returns
    -------
    A string as per psi4 input.

    """
    elements = periodic_table(atomic_nums)
    psi4_str = f"\n{charge} {multip}\n"
    for i, atom in enumerate(coords):
        psi4_str += f"{elements[i]} {atom[0]} {atom[1]} {atom[2]}\n"
    psi4_str += "units angstrom\n"
    return psi4_str


def obabel_energy(ff, obmol):
    """Use Openbabel to calculate the energy of a molecule.

    Parameters
    ----------
    ff : str
        The name of the forcefield to use. Should be one of:
        'gaff', 'ghemical', 'mmff94', 'mmff94s', 'uff'
    obmol : openbabel.OBMol object
        An openbabel molecule for which to calculate
        the energy.

    Notes
    -----
    This function attempts to implement the obenergy function.

    Returns
    -------
    energy : float
        The energy of the input molecule using ff forcefield
        in kcal/mol.

    """
    if ff not in pybel.forcefields:
        raise MethodError(f"Forcefield unavailable in Openbabel: {ff}")
    ff_instance = pybel.ob.OBForceField.FindForceField(ff)
    result = ff_instance.Setup(obmol)
    if not result:
        raise MethodError("Unable to setup forcefield for molecule")
    energy = ff_instance.Energy(False)
    return energy
