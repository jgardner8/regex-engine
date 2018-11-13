import adt
from utils import DefaultDict

class NFAState:
    def __init__(self, is_accepting=False):
        self.is_accepting = is_accepting
        self.on_char = DefaultDict(list)
        self.on_epsilon = []

    def on_unmatched_char(self, state=None):
        '''Used by AnyChar and inverted CharClass to avoid enumerating every possible character'''
        if state:
            self.on_char.default_factory = lambda: [state]
        else:
            return self.on_char.default_factory()

    def add_char_edge(self, char, state):
        assert len(char) == 1, 'char must be a string of length 1, got {0}'.format(char)
        if char in self.on_char:
            self.on_char[char].append(state)
        else:
            self.on_char[char] = [state]

    def add_epsilon_edge(self, state):
        self.on_epsilon.append(state)

    def matches(self, s):
        return self._matches(s, [])

    def _matches(self, s, visited):
        if (self, len(s)) in visited:
            return False
        visited.append( (self, len(s)) )

        if len(s) == 0:
            if self.is_accepting:
                return True
        else:
            if any(state._matches(s[1:], visited) for state in self.on_char[s[0]]):
                return True

        return any(state._matches(s, visited) for state in self.on_epsilon)

class NFA:
    def __init__(self, entry, exit):
        self.entry = entry
        self.exit = exit

    def matches(self, s):
        return self.entry.matches(s)

def from_ast(regex):
    if type(regex) == adt.Or:
        nfa_a, nfa_b = from_ast(regex.regex_a), from_ast(regex.regex_b)
        
        entry = NFAState()
        exit = NFAState(is_accepting=True)
        nfa_a.exit.is_accepting = False
        nfa_b.exit.is_accepting = False

        entry.add_epsilon_edge(nfa_a.entry)
        entry.add_epsilon_edge(nfa_b.entry)
        nfa_a.exit.add_epsilon_edge(exit)
        nfa_b.exit.add_epsilon_edge(exit)

        return NFA(entry, exit)

    elif type(regex) == adt.Sequence:
        nfa_a, nfa_b = from_ast(regex.regex_a), from_ast(regex.regex_b)

        nfa_a.exit.is_accepting = False
        nfa_b.exit.is_accepting = True
        nfa_a.exit.add_epsilon_edge(nfa_b.entry)
        
        return NFA(nfa_a.entry, nfa_b.exit)

    elif type(regex) == adt.ZeroOrMore:
        nfa = from_ast(regex.regex)

        nfa.exit.add_epsilon_edge(nfa.entry)
        nfa.entry.add_epsilon_edge(nfa.exit)

        return nfa

    elif type(regex) == adt.Optional:
        nfa = from_ast(regex.regex)

        nfa.entry.add_epsilon_edge(nfa.exit)

        return nfa

    elif type(regex) == adt.Char:
        entry = NFAState()
        exit = NFAState(is_accepting=True)
        entry.add_char_edge(regex.char, exit)
        return NFA(entry, exit)

    elif type(regex) == adt.AnyChar:
        entry = NFAState()
        exit = NFAState(is_accepting=True)
        entry.on_unmatched_char(exit)
        return NFA(entry, exit) 

    elif type(regex) == adt.CharClass:
        entry = NFAState()
        exit = NFAState(is_accepting=True)

        if not regex.invert:
            for str_or_char_range in regex.strs_or_char_ranges:
                for char in str_or_char_range:
                    entry.add_char_edge(char, exit)
        else:
            entry.on_unmatched_char(exit)
            for str_or_char_range in regex.strs_or_char_ranges:
                for char in str_or_char_range:
                    entry.on_char[char] = []

        return NFA(entry, exit)

    elif type(regex) == adt.Epsilon:
        entry = NFAState()
        exit = NFAState(is_accepting=True)
        entry.add_epsilon_edge(exit)
        return NFA(entry, exit)

    raise ValueError("Can't generate NFA for unknown type: {0}".format(regex))