import unittest
import nfa
import dfa
from adt import *
from parser import parse_regex

class MultipleMethodsTester:
    def __init__(self, unittest, regex):
        self.regex = regex
        self.ast = parse_regex(regex)
        self.nfa = nfa.from_ast(self.ast)
        self.dfa = dfa.from_nfa(self.nfa)
        self.unittest = unittest

    def _failure_details(self, s, invert=False):
        return 'method failed: "{0}" did {1}match "{2}"'.format(self.regex, '' if invert else 'not ', s)

    def assert_matches(self, s):
        self.unittest.assertTrue(self.ast.matches(s), 'Derivative {0}'.format(self._failure_details(s)))
        self.unittest.assertTrue(self.nfa.matches(s), 'NFA {0}'.format(self._failure_details(s)))
        self.unittest.assertTrue(self.dfa.matches(s), 'DFA {0}'.format(self._failure_details(s)))

    def assert_not_matches(self, s):
        self.unittest.assertFalse(self.ast.matches(s), 'Derivative {0}'.format(self._failure_details(s, True)))
        self.unittest.assertFalse(self.nfa.matches(s), 'NFA {0}'.format(self._failure_details(s, True)))  
        self.unittest.assertFalse(self.dfa.matches(s), 'DFA {0}'.format(self._failure_details(s, True)))  

class TestEndToEnd(unittest.TestCase):         
    def test_end_to_end_basic_email_address(self):
        tester = MultipleMethodsTester(self, '.+@.+\..+')
        tester.assert_matches('email@address.com')
        tester.assert_not_matches('@address.com')
        tester.assert_not_matches('email@.com')
        tester.assert_not_matches('email@address.')
        tester.assert_not_matches('email@address')
        tester.assert_not_matches('@.')

    def test_end_to_end_complex_email_address(self):
        # Regex from W3C, implemented in <input type="email">
        # Only modification is to remove ?: from start of final set of parenthesis, which would 
        # usually create a non-capturing group. Whether the group captures or not makes no difference 
        # to matching, only to getting data from the capturing groups, which we don't support anyway.
        # Therefore the regex is equivalent to the W3C regex for our purposes.
        tester = MultipleMethodsTester(self, '[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*')
        tester.assert_matches('email@address.com')
        tester.assert_matches('email@address.com.au')
        tester.assert_matches('firstname.lastname@domain-name.com.au')
        tester.assert_not_matches('@address.com')
        tester.assert_not_matches('email@.com')
        tester.assert_not_matches('email@address.')
        tester.assert_matches('email@address')
        tester.assert_matches('email@address.com.au')
        tester.assert_not_matches('@.')

    def test_end_to_end_phone_number(self):
        # Australian home phone number, optional area code in brackets, followed by 4 digits, a dash and 4 more digits
        equivalent_testers = (
            MultipleMethodsTester(self, '(\(0[0-9]\))?[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
            MultipleMethodsTester(self, '(\(0\d\))?\d\d\d\d-\d\d\d\d')
        )
        self.assertEqual(equivalent_testers[0].ast, equivalent_testers[1].ast, 'asts are not the same')

        for tester in equivalent_testers:
            tester.assert_matches('(03)9743-9939')
            tester.assert_matches('9743-9939')
            tester.assert_not_matches('039743-9939')
            tester.assert_not_matches('(0397439939')
            tester.assert_not_matches('03)97439939')
            tester.assert_not_matches('(0)97439939')
            tester.assert_not_matches('(13)9743-9939')
            tester.assert_not_matches('97439939')

    def test_end_to_end_optional(self):
        tester = MultipleMethodsTester(self, 'a(bcd)?e')
        tester.assert_matches('abcde')
        tester.assert_matches('ae')
        tester.assert_not_matches('bcde')
        tester.assert_not_matches('abcd')
        tester.assert_not_matches('abce')

        tester = MultipleMethodsTester(self, '(a|b?)c')
        tester.assert_matches('ac')
        tester.assert_matches('bc')
        tester.assert_matches('c')
        tester.assert_not_matches('a')
        tester.assert_not_matches('b')
        tester.assert_not_matches('abc')
        tester.assert_not_matches('ab')

        tester = MultipleMethodsTester(self, 'a(b|c?)')
        tester.assert_matches('a')
        tester.assert_matches('ab')
        tester.assert_matches('ac')
        tester.assert_not_matches('b')
        tester.assert_not_matches('c')
        tester.assert_not_matches('bc')

        tester = MultipleMethodsTester(self, 'a(b|c?)d')
        tester.assert_matches('abd')
        tester.assert_matches('ad')
        tester.assert_matches('acd')
        tester.assert_not_matches('abcd')
        tester.assert_not_matches('accd')

        tester = MultipleMethodsTester(self, 'Feb(ruary)? .+(st|nd|rd|th)?')
        tester.assert_matches('Feb 2')
        tester.assert_matches('Feb 2nd')
        tester.assert_matches('Feb 21')
        tester.assert_matches('Feb 21st')
        tester.assert_matches('Feb 22nd')
        tester.assert_matches('February 22')
        tester.assert_matches('February 23rd')
        tester.assert_not_matches('Feb')
        tester.assert_not_matches('Feb ')

    def test_end_to_end_char_class(self):
        tester = MultipleMethodsTester(self, '[bc]')
        tester.assert_matches('b')
        tester.assert_matches('c')
        tester.assert_not_matches('a')
        tester.assert_not_matches('d')

        tester = MultipleMethodsTester(self, 'a[bc]d')
        tester.assert_matches('abd')
        tester.assert_matches('acd')
        tester.assert_not_matches('ad')
        tester.assert_not_matches('abcd')
        tester.assert_not_matches('bc')
        tester.assert_not_matches('ab')
        tester.assert_not_matches('cd')

        tester = MultipleMethodsTester(self, 'a[C-E]d')
        tester.assert_matches('aCd')
        tester.assert_matches('aDd')
        tester.assert_matches('aEd')
        tester.assert_not_matches('aBd')
        tester.assert_not_matches('aFd')
        tester.assert_not_matches('acd')
        tester.assert_not_matches('add')
        tester.assert_not_matches('aed')
        
        tester = MultipleMethodsTester(self, 'a[1-3]d')
        tester.assert_matches('a1d')
        tester.assert_matches('a2d')
        tester.assert_matches('a3d')
        tester.assert_not_matches('a0d')
        tester.assert_not_matches('a4d')
        
        tester = MultipleMethodsTester(self, 'a[b-dB-D]d')
        tester.assert_matches('abd')
        tester.assert_matches('acd')
        tester.assert_matches('add')
        tester.assert_matches('aBd')
        tester.assert_matches('aCd')
        tester.assert_matches('aDd')
        tester.assert_not_matches('aad')
        tester.assert_not_matches('aAd')
        tester.assert_not_matches('aed')
        tester.assert_not_matches('aEd')
        
        tester = MultipleMethodsTester(self, 'a[|$\-b-d]d')
        tester.assert_matches('a|d')
        tester.assert_matches('a$d')
        tester.assert_matches('abd')
        tester.assert_matches('acd')
        tester.assert_matches('add')
        tester.assert_matches('a-d')

        tester = MultipleMethodsTester(self, 'a[^|$b-d\-]d')
        tester.assert_not_matches('a|d')
        tester.assert_not_matches('a$d')
        tester.assert_not_matches('abd')
        tester.assert_not_matches('acd')
        tester.assert_not_matches('add')
        tester.assert_not_matches('a-d')
        tester.assert_matches('a/d')
        tester.assert_matches('a\d')
        tester.assert_matches('aad')
        tester.assert_not_matches('ad')

        # Escaped caret (^)
        tester = MultipleMethodsTester(self, 'a[\^]d')
        tester.assert_matches('a^d')

        # Carets that aren't the first char of a character class don't need to be
        # escaped, as it's not ambiguous whether they mean "not".
        tester = MultipleMethodsTester(self, 'a[^^]d')
        tester.assert_not_matches('a^d')
        tester = MultipleMethodsTester(self, 'a[b^c]d')
        tester.assert_matches('abd')
        tester.assert_matches('a^d')
        tester.assert_matches('acd')

        # Dashes (-) at the start or end of a character class don't need to be 
        # escaped, as it's not ambiguous whether they're part of a CharRange.
        tester = MultipleMethodsTester(self, 'a[-de]f')
        tester.assert_matches('a-f')
        tester.assert_matches('adf')
        tester.assert_matches('aef')
        tester = MultipleMethodsTester(self, 'a[de-]f')
        tester.assert_matches('a-f')
        tester.assert_matches('adf')
        tester.assert_matches('aef')
        tester = MultipleMethodsTester(self, 'a[^-de]f')
        tester.assert_not_matches('a-f')
        tester.assert_not_matches('adf')
        tester.assert_not_matches('aef')
        tester.assert_matches('a_f')

    def test_end_to_end_char_class_shorthand(self):
        tester = MultipleMethodsTester(self, '\w\w\w')
        tester.assert_matches('asd')
        tester.assert_matches('a_d')
        tester.assert_not_matches('asdd')
        tester.assert_not_matches('as')
        tester.assert_not_matches('a s')

        tester = MultipleMethodsTester(self, '\W')
        tester.assert_matches(' ')
        tester.assert_matches('/')
        tester.assert_not_matches('a')
        tester = MultipleMethodsTester(self, '\W\W\W')
        tester.assert_matches('   ')
        tester.assert_matches('/*$')
        tester.assert_not_matches('add')

        tester = MultipleMethodsTester(self, '\s\S')
        tester.assert_matches(' s')
        tester.assert_matches('\n$')
        tester.assert_matches('\n\\')
        tester.assert_not_matches('aa')
        tester.assert_not_matches('a ')
