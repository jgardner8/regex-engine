import unittest
from nfa import from_ast
from adt import *
from parser import parse_regex

class TestNfa(unittest.TestCase):
    def test_matches_char(self):
        nfa = from_ast(Char('c'))
        self.assertTrue(nfa.matches('c'))
        self.assertFalse(nfa.matches('b'))
        self.assertFalse(nfa.matches('cc'))
        self.assertFalse(nfa.matches(''))

    def test_matches_sequence(self):
        nfa = from_ast(Sequence(Char('a'), Char('b')))
        self.assertTrue(nfa.matches('ab'))
        self.assertFalse(nfa.matches('a'))
        self.assertFalse(nfa.matches('b'))
        self.assertFalse(nfa.matches('abb'))
        self.assertFalse(nfa.matches('aab'))

    def test_matches_or(self):
        nfa = from_ast(Or(Char('a'), Char('b')))
        self.assertTrue(nfa.matches('a'))
        self.assertTrue(nfa.matches('b'))
        self.assertFalse(nfa.matches('c'))
        self.assertFalse(nfa.matches(''))

    def test_matches_zero_or_more(self):
        nfa = from_ast(ZeroOrMore(Char('a')))
        self.assertTrue(nfa.matches(''))
        self.assertTrue(nfa.matches('a'))
        self.assertTrue(nfa.matches('aa'))
        self.assertTrue(nfa.matches('aaaaaaa'))
        self.assertFalse(nfa.matches('b'))

    def test_matches_optional(self):
        nfa = from_ast(Optional(Char('a')))
        self.assertTrue(nfa.matches(''))
        self.assertTrue(nfa.matches('a'))
        self.assertFalse(nfa.matches('aa'))
        self.assertFalse(nfa.matches('b'))

    def test_matches_any_char(self):
        nfa = from_ast(AnyChar())
        self.assertTrue(nfa.matches('a'))
        self.assertTrue(nfa.matches('b'))
        self.assertFalse(nfa.matches(''))
        self.assertFalse(nfa.matches('ab'))

    def test_matches_char_class(self):
        nfa = from_ast(CharClass(invert=False, strs_or_char_ranges=['b', CharRange('c', 'e')]))
        self.assertTrue(nfa.matches('b'))
        self.assertTrue(nfa.matches('c'))
        self.assertTrue(nfa.matches('d'))
        self.assertTrue(nfa.matches('e'))
        self.assertFalse(nfa.matches('a'))
        self.assertFalse(nfa.matches('f'))
        self.assertFalse(nfa.matches(''))
        self.assertFalse(nfa.matches('bb'))

        nfa = from_ast(CharClass(invert=True, strs_or_char_ranges=['b', CharRange('c', 'e')]))
        self.assertFalse(nfa.matches('b'))
        self.assertFalse(nfa.matches('c'))
        self.assertFalse(nfa.matches('d'))
        self.assertFalse(nfa.matches('e'))
        self.assertTrue(nfa.matches('a'))
        self.assertTrue(nfa.matches('f'))
        self.assertFalse(nfa.matches(''))
        self.assertFalse(nfa.matches('bb'))

    def test_matches_epsilon(self):
        nfa = from_ast(Epsilon())
        self.assertTrue(nfa.matches(''))
        self.assertFalse(nfa.matches(' '))
        self.assertFalse(nfa.matches('a'))

    def test_matches_complex_1(self):
        nfa = from_ast(parse_regex('a?b*(c|d)'))
        self.assertTrue(nfa.matches('abc'))
        self.assertTrue(nfa.matches('abd'))
        self.assertTrue(nfa.matches('bc'))
        self.assertTrue(nfa.matches('bd'))
        self.assertTrue(nfa.matches('c'))
        self.assertTrue(nfa.matches('d'))
        self.assertTrue(nfa.matches('bbbc'))
        self.assertTrue(nfa.matches('bbbd'))

    def test_matches_complex_2(self):
        nfa = from_ast(parse_regex('(ab)?(cde)*'))
        self.assertTrue(nfa.matches(''))
        self.assertTrue(nfa.matches('ab'))
        self.assertTrue(nfa.matches('cde'))
        self.assertTrue(nfa.matches('abcde'))
        self.assertTrue(nfa.matches('abcdecde'))
        self.assertTrue(nfa.matches('abcdecdecde'))
        self.assertFalse(nfa.matches('a'))
        self.assertFalse(nfa.matches('c'))
        self.assertFalse(nfa.matches('cd'))
        self.assertFalse(nfa.matches('de'))
