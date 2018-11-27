
import numpy as np
from kaplan.ring import EmptyRingError
from kaplan.mutations import generate_children

def run_tournament(t_size, num_muts, num_swaps, ring,
                   current_mev):
    # check ring has enough pmems for a tournament
    if t_size > ring.num_filled:
        raise EmtpyRingError("Not enough pmems to run a tournament.")

    # choose random slots for a tournament
    selected_pmems = select_pmems(t_size, ring)

    # select parents by fitness
    parents = select_parents(selected_pmems, ring)
    parent1 = ring.pmems[parents[0]].dihedrals
    parent2 = ring.pmems[parents[1]].dihedrals

    # generate children
    children = generate_children(parent1, parent2, num_muts,
                                 num_swaps, current_mev)

    # put children in ring
    ring.update(parents[0], children[1])
    ring.update(parents[1], children[0])

def select_pmems(number, ring):
    """Randomly selected pmems.

    Parameters
    ----------
    number : int
        How many pmems to pick.
    ring : object

    Note
    ----
    Maybe move this to the ring as a method. Or turn
    into a generator (calling next on the ring returns
    a random pmem).

    """
    selection = []
    for pmem in range(number):
        # choose random slot
        choice = np.random.randint(0, ring.num_slots)
        # if the slot is empty, keep picking another random one
        while ring.pmems[choice] is None:
            choice = np.random.randint(0, ring.num_slots)
        selected.append(choice)
    return selection

def select_parents(selected_pmems, ring):
    """Sort pmems by fitness values, choose best 2.

    Parameters
    ----------
    selected_pmems : list
        The indices of the ring that are in the tournament.

    ring : object
        Instance of Ring class.

    Returns
    -------
    tuple : int,int
        Indices of two best pmems to be used as parents.

    """
    fit_vals = np.array([ring.pmems[i].fitness for i in selected_pmems])
    # from here:
    # https://stackoverflow.com/questions/6910641/how-do-i-get-indices-of-n-maximum-values-in-a-numpy-array
    # use numpy to get the two best fitness value indices
    # from the list and link it to ring index
    parents = (selected_pmems[parent] for parent in np.argpartition(fit_vals, -2)[-2:])
    return parents

