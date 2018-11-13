import adt
from utils import raise_if_not

def sequence_tree_from_regexes(regexes):
    raise_if_not(len(regexes) >= 2, 'Regexes must contain at least two objects to build a Sequence')

    sequence = regexes[0]
    for i in range(1, len(regexes)):
        sequence = adt.Sequence(sequence, regexes[i])
    return sequence

def char_sequence_from_str(s):
    return sequence_tree_from_regexes([adt.Char(c) for c in s])
