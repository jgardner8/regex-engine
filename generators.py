import adt
import random
import string
from collections import deque

def printable_chars_except(chars):
    return [c for c in string.printable if c not in chars]

def printable_char():
    return random.choice(string.printable)

def letter():
    return random.choice(string.ascii_letters)

def lowercase_letter():
    return random.choice(string.ascii_lowercase)

def uppercase_letter():
    return random.choice(string.ascii_uppercase)

def digit():
    return random.choice(string.digits)

def letter_or_digit():
    return random.choice(string.ascii_letters + string.digits)

def boolean():
    return random.random() < 0.5

def char_range():
    while True:
        a = letter_or_digit()
        if str.islower(a):
            b = lowercase_letter()
        elif str.isupper(a):
            b = uppercase_letter()
        elif str.isdigit(a):
            b = digit()
        else:
            raise ValueError('Unexpected result from letter_or_digit(): {0}'.format(a))

        try:
            return adt.CharRange(a, b)
        except ValueError:
            pass # invalid range, a >= b

def ast():
    MAX_DEPTH = 4
    ODDS_PRINTABLE_CHAR_OVER_CHAR_RANGE = 0.5
    ODDS_NO_MORE_CHARS_IN_CHAR_RANGE = 0.4

    def _ast(max_depth):
        branch_adts = [adt.Or, adt.Sequence, adt.ZeroOrMore, adt.Optional]
        leaf_adts = [adt.Char, adt.AnyChar, adt.CharClass]
        adt_choice = random.choice(branch_adts if max_depth > 1 else leaf_adts)

        if adt_choice == adt.Or:
            return adt.Or(_ast(max_depth-1), _ast(max_depth-1))
        elif adt_choice == adt.Sequence:
            return adt.Sequence(_ast(max_depth-1), _ast(max_depth-1))
        elif adt_choice == adt.ZeroOrMore:
            return adt.ZeroOrMore(_ast(max_depth-1))
        elif adt_choice == adt.Optional:
            return adt.Optional(_ast(max_depth-1))
        elif adt_choice == adt.Char:
            return adt.Char(printable_char())
        elif adt_choice == adt.AnyChar:
            return adt.AnyChar()
        elif adt_choice == adt.CharClass:
            strs_or_char_ranges = []
            while True:
                strs_or_char_ranges.append(printable_char() if random.random() < ODDS_PRINTABLE_CHAR_OVER_CHAR_RANGE else char_range())

                if random.random() < ODDS_NO_MORE_CHARS_IN_CHAR_RANGE:
                    break

            return adt.CharClass(invert=boolean(), strs_or_char_ranges=strs_or_char_ranges)
        raise ValueError("Can't generate random regex for unknown type: {0}".format(adt_choice))

    return _ast(random.randint(1, MAX_DEPTH))

def matching_str(regex):
    ODDS_NO_MORE_MATCHES_ZERO_OR_MORE = 0.2
    MAX_MATCHES_ZERO_OR_MORE = 3

    if type(regex) == adt.Or:
        return random.choice([matching_str(regex.regex_a), matching_str(regex.regex_b)])
    elif type(regex) == adt.Sequence:
        return matching_str(regex.regex_a) + matching_str(regex.regex_b)
    elif type(regex) == adt.ZeroOrMore:
        match = []
        for _ in range(MAX_MATCHES_ZERO_OR_MORE):
            if random.random() < ODDS_NO_MORE_MATCHES_ZERO_OR_MORE:
                break
            match.append(matching_str(regex.regex))
        return ''.join(match)
    elif type(regex) == adt.Optional:
        return random.choice(['', matching_str(regex.regex)])
    elif type(regex) == adt.Char:
        return regex.char
    elif type(regex) == adt.AnyChar:
        return printable_char()
    elif type(regex) == adt.CharClass:
        chars = []
        for str_or_char_range in regex.strs_or_char_ranges:
            for char in str_or_char_range:
                chars.append(char)

        if regex.invert:
            chars = printable_chars_except(chars)

        return random.choice(chars)
    elif type(regex) == adt.Epsilon:
        return ''
    elif type(regex) == adt.NullRegex:
        raise ValueError('matching_str(NullRegex)')
    raise ValueError("Can't generate matching string for unknown type: {0}".format(type(regex)))

def equivalence_classes(regex):
    def prepend(value, eq_classes):
        for eq_class in eq_classes:
            eq_class.appendleft(value)

    MULTIPLE_MATCH_ZERO_OR_MORE = (2, 3)

    if type(regex) == adt.Or:
        return equivalence_classes(regex.regex_a) + equivalence_classes(regex.regex_b)
    elif type(regex) == adt.Sequence:
        a = equivalence_classes(regex.regex_a)
        b = equivalence_classes(regex.regex_b)
        for eq_class in b:
            prepend(a, b)
    elif type(regex) == adt.ZeroOrMore:
        # TODO: can't do multiple matches
        eq_classes = equivalence_classes(regex.regex)
        return prepend('', eq_classes)
    elif type(regex) == adt.Optional:
        return prepend('', equivalence_classes(regex.regex))
    elif type(regex) == adt.Char:
        return deque(['', regex.char, random.choice(printable_chars_except(regex.char))])
    elif type(regex) == adt.AnyChar:
        return deque(['', printable_char()])
    elif type(regex) == adt.CharClass:
        # return deque(['', random.choice(regex.chars), random.choice(printable_chars_except(regex.chars))])
        pass
    elif type(regex) == adt.Epsilon:
        return deque(['', printable_char()])
    elif type(regex) == adt.NullRegex:
        raise ValueError('equivalence_classes(NullRegex)')
    raise ValueError("Can't generate matching string for unknown type: {0}".format(type(regex)))