import unittest
from adt import *
from adt_fancy_constructors import *
from parser import parse_regex

class TestParser(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(
            parse_regex(''),
            Epsilon()
        )
        
        self.assertEqual(
            parse_regex('abcd'),
            char_sequence_from_str('abcd'),
            'Simple'
        )

        self.assertEqual(
            parse_regex('ab|cd'),
            Or(char_sequence_from_str('ab'), char_sequence_from_str('cd')),
            'Or'
        )

        self.assertEqual(
            parse_regex('a(b|c)d'),
            sequence_tree_from_regexes([Char('a'), Or(Char('b'), Char('c')), Char('d')]),
            'Or with precedence'
        )

        self.assertEqual(
            parse_regex('a(b*|c)d'),
            sequence_tree_from_regexes([Char('a'), Or(ZeroOrMore(Char('b')), Char('c')), Char('d')]),
            'Kleene star'
        )

        self.assertEqual(
            parse_regex('a(b+|c)d'),
            sequence_tree_from_regexes([Char('a'), Or(Sequence(Char('b'), ZeroOrMore(Char('b'))), Char('c')), Char('d')]),
            'Kleene plus'
        )

        self.assertEqual(
            parse_regex('a(b*|.)d'),
            sequence_tree_from_regexes([Char('a'), Or(ZeroOrMore(Char('b')), AnyChar()), Char('d')]),
            'Any character'
        )

        self.assertEqual(
            parse_regex('a(b*|\.)d'),
            sequence_tree_from_regexes([Char('a'), Or(ZeroOrMore(Char('b')), Char('.')), Char('d')]),
            'Escaping: period character'
        )

        self.assertEqual(
            parse_regex('\+-_\.\(\)'),
            char_sequence_from_str('+-_.()'),
            'Escaping: lots'
        )

        self.assertEqual(
            parse_regex('a{15}'),
            sequence_tree_from_regexes([Char('a')]*15),
            'Parse {15} quantifier'
        )

        self.assertEqual(
            parse_regex('a{15,}'),
            sequence_tree_from_regexes([Char('a')]*15 + [ZeroOrMore(Char('a'))]),
            'Parse {15,} quantifier'
        )

        self.assertEqual(
            parse_regex('a{15,17}'),
            sequence_tree_from_regexes([Char('a')]*15 + [Optional(Char('a'))]*2),
            'Parse {15,17} quantifier'
        )
