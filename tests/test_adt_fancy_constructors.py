import unittest
from adt import *
from adt_fancy_constructors import *

class TestAdtFancyConstructors(unittest.TestCase):
    def test_sequence_tree_from_regexes(self):
        with self.assertRaises(ValueError):
            sequence_tree_from_regexes([Char('a')]) # need two regexes for a sequence

        self.assertEqual(
            sequence_tree_from_regexes([Char('a'), Char('b')]), 
            Sequence(Char('a'), Char('b'))
        )

        self.assertEqual(
            sequence_tree_from_regexes([Char('a'), Char('b'), Char('c')]),
            Sequence(Sequence(Char('a'), Char('b')), Char('c'))
        )

        self.assertEqual(
            sequence_tree_from_regexes([Char('a'), Char('b'), Char('c'), Char('d')]),
            Sequence(Sequence(Sequence(Char('a'), Char('b')), Char('c')), Char('d'))
        )

    def test_char_sequence_from_str(self):
        self.assertEqual(
            char_sequence_from_str('abcd'),
            Sequence(Sequence(Sequence(Char('a'), Char('b')), Char('c')), Char('d'))
        )