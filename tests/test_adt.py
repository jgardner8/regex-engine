import unittest
from adt import *
from adt_fancy_constructors import *

class TestAdt(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(
            Epsilon().matches(''), 
            'Empty string'
        )

        self.assertTrue(
            Char('a').matches('a'),
            'Single character'
        )

        self.assertTrue(
            Or(Char('a'), Char('b')).matches('a'),
            'Or left side'
        )

        self.assertTrue(
            Or(Char('a'), Char('b')).matches('b'),
            'Or right side'
        )

        self.assertTrue(
            Sequence(Char('a'), Char('b')).matches('ab'),
            'Sequence of two chars'
        )

        self.assertTrue(
            Sequence(Char('a'), ZeroOrMore(Char('b'))).matches('abbb'),
            'Kleene star'
        )

        self.assertFalse(
            Sequence(Char('a'), ZeroOrMore(Char('b'))).matches('abzbb'),
            'Kleene star negative'
        )

        self.assertTrue(
            Sequence(Char('a'), ZeroOrMore(Or(Char('b'), Char('z')))).matches('abzbb'),
            'Kleene star on an Or expression'
        )

    def test_optional(self):
        self.assertTrue(
            Optional(Char('a')).matches(''),
            'Optional matched with empty string'
        )

        self.assertTrue(
            Optional(Char('a')).matches('a'),
            'Optional matched with value'
        )

        self.assertFalse(
            Optional(Char('a')).matches('b'),
            "Optional matched with incorrect value"
        )

        self.assertTrue(
            Optional(Sequence(Char('a'), Char('b'))).matches('ab'),
            'Optional sequence'
        )

    def test_derivative(self):
        self.assertEqual(Char('a').derivative('a'), Epsilon())
        self.assertEqual(Char('a').derivative('b'), NullRegex())

        self.assertEqual(
            char_sequence_from_str('ab').derivative('a'), 
            Char('b')
        )

        self.assertEqual(
            char_sequence_from_str('ab').derivative('b'),
            NullRegex()
        )
        
        self.assertEqual(
            Or(
                Sequence(Char('a'), Char('b')), 
                Sequence(Char('a'), ZeroOrMore(Char('c')))
            ).derivative('a'), 
            Or(Char('b'), ZeroOrMore(Char('c')))
        )