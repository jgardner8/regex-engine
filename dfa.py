import generators
from utils import lpartition, find, DefaultDict
from collections import namedtuple
from nfa import NFAState

class DFAState:
    def __init__(self, is_accepting=False):
        self.is_accepting = is_accepting
        self.on_char = {}

    def is_trap(self):
        '''A state is a trap if it is not accepting and it has no exits except looping back on itself'''
        return not self.is_accepting and self.on_char == {} and self.on_char['random-val'] == self

    def on_unmatched_char(self, state=None):
        '''Used by AnyChar and inverted CharClass to avoid enumerating every possible character'''
        if state:
            assert type(self.on_char) == dict, 'on_unmatched_char is already set'
            self.on_char = DefaultDict(lambda: state, self.on_char)
        else:
            assert type(self.on_char) == DefaultDict, 'on_unmatched_char is not set'
            return self.on_char.default_factory()

    def add_edge(self, char, state):
        assert len(char) == 1, 'char must be a string of length 1, got: {0}'.format(char)
        assert char not in self.on_char, 'Already have an edge for char: {0}'.format(char)
        self.on_char[char] = state

    def matches(self, s):
        return self.is_accepting if len(s) == 0 else self.on_char[s[0]].matches(s[1:])

    def find_longest_match(self, consumed, left):
        ''' Find longest possible match for string `left` given we've already traversed chars `consumed` '''
        state = self
        biggest_match = None

        while left and not state.is_trap():
            if state.is_accepting:
                biggest_match = consumed

            consumed += left[0]
            state = state.on_char[left[0]]
            left = left[1:]

        return biggest_match

class DFA:
    def __init__(self, entry):
        self.entry = entry

    def matches(self, s):
        ''' True if DFA matches the entire string s '''
        return self.entry.matches(s)

    def find_subset_matches(self, s):
        ''' For each position in s, finds the longest possible match, returning a list of matches '''
        matches = []
        while s:
            match = self.entry.find_longest_match('', s)
            if match not in (None, ''): # None is non-match, '' is match of length 0 (e.g. a* against b)
                if not any(match in m for m in matches): # subset of something we've previously found
                    matches.append(match)
            s = s[1:]
        return matches

def from_nfa(nfa):
    '''Create a DFA from an NFA, i.e. return a version of nfa that is deterministic'''
    def accessible_without_input(nfa_state_set):
        '''Aka ε-Closure. Finds all the states that can be found with epsilon edges'''
        def _accessible_without_input(nfa_state, discovered):
            if nfa_state in discovered:
                return set()
            discovered.add(nfa_state)
            
            for state in nfa_state.on_epsilon:
                discovered = discovered.union(_accessible_without_input(state, discovered))
            return discovered

        on_epsilon = []
        for state in nfa_state_set:
            on_epsilon.extend(_accessible_without_input(state, set()))
        return tuple(on_epsilon)

    def all_possible_moves(nfa_state_set):
        ''' 
        Returns a dictionary mapping a char to all states that can be traversed to with that char from nfa_state_set.
        An nfa_state_set already includes all the states that can be reached without input, so all of the possible 
        moves for a given char is defined as:
            - Every state you can reach with that char (on_char[char] and on_unmatched_char)
            - Every state you can reach without input from those states (accessible_without_input(on_char[char]))
        '''
        # Inverted states have on_unmatched_char set to a state; used to model AnyChar or an inverted CharClass
        non_inverted_states, inverted_states = lpartition(nfa_state_set, lambda s: s.on_unmatched_char() == [])
        on_char = DefaultDict(set)
        on_unmatched_char = set()
        
        # Non inverted states (move by char)
        for state in non_inverted_states:
            for char in state.on_char.keys():
                on_char[char] = on_char[char].union(state.on_char[char])

        # Inverted states (move by not char)
        for state in inverted_states:
            for char in [c for c in state.on_char.keys() if c not in on_char.keys()]:
                assert state.on_char[char] == [], "An inverted state shouldn't have edges leading to real states"
                on_char[char] = set([nfa_trap_state])

        for state in inverted_states:
            assert len(state.on_unmatched_char()) == 1, "An inverted state should have only one state to move to on_unmatched_char"
            on_unmatched_char.add(state.on_unmatched_char()[0])
            for char in [c for c in on_char.keys() if c not in state.on_char]:
                on_char[char].add(state.on_unmatched_char()[0])

        # Epsilon moves (move without input)
        for char in on_char.keys():
            on_char[char] = on_char[char].union(accessible_without_input(on_char[char]))
        on_unmatched_char = on_unmatched_char.union(accessible_without_input(on_unmatched_char))

        # Convert to tuples, as these are state_sets
        return {c: tuple(on_char[c]) for c in on_char.keys()}, tuple(on_unmatched_char)

    def create_dfa(nfa_state_sets, edges, start_state_set):
        '''Create the DFA state graph based on the NFA state sets and edges identified'''
        def find_dfa_state(state_set):
            return find(lambda pair: pair[0] == state_set, dfa_states)[1]

        # Create DFA state objects and edges
        dfa_states = [(state_set, DFAState()) for state_set in nfa_state_sets]
        for edge in edges:
            from_state = find_dfa_state(edge.from_state_set)
            to_state = find_dfa_state(edge.to_state_set)
            if edge.char == 'default':
                from_state.on_unmatched_char(to_state)
            else:
                from_state.add_edge(edge.char, to_state)

        # Set accepting states
        for state_set in nfa_state_sets:
            if any(state.is_accepting for state in state_set):
                find_dfa_state(state_set).is_accepting = True

        return DFA(find_dfa_state(start_state_set))

    def add_state_set(char, from_state_set, to_state_set):
        if to_state_set not in processed_state_sets:
            queued_state_sets.add(to_state_set)
        edges.append(Edge(char, from_state_set, to_state_set))

    nfa_trap_state = NFAState()
    
    start_state_set = accessible_without_input([nfa.entry])
    processed_state_sets = []
    queued_state_sets = set( (start_state_set,) )

    Edge = namedtuple('Edge', ['char', 'from_state_set', 'to_state_set'])
    edges = []    

    while queued_state_sets:
        nfa_state_set = queued_state_sets.pop()
        processed_state_sets.append(nfa_state_set)

        on_char, on_unmatched_char = all_possible_moves(nfa_state_set)
        add_state_set(char='default', from_state_set=nfa_state_set, to_state_set=on_unmatched_char)
        for char in on_char.keys():
            add_state_set(char=char, from_state_set=nfa_state_set, to_state_set=on_char[char])

    return create_dfa(processed_state_sets, edges, start_state_set)