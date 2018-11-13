'''Test that the evaluation is deterministic, i.e. repeatable'''
import unittest
import nfa
import dfa
from parser import parse_regex

class TestDeterministic(unittest.TestCase):
    def test_derivative_matches(self):
        ast = parse_regex('o|oa')
        for i in range(100):
            assert ast.matches('o'), 'derivative.matches attempt: {0}'.format(i)

    def test_nfa_matches(self):
        ast = parse_regex('o|oa')
        nfa_ = nfa.from_ast(ast)
        for i in range(100):
            assert nfa_.matches('o'), 'nfa.matches attempt: {0}'.format(i)

    def test_dfa_matches(self):
        ast = parse_regex('o|oa')
        nfa_ = nfa.from_ast(ast)
        dfa_ = dfa.from_nfa(nfa_)
        for i in range(100):
            assert dfa_.matches('o'), 'dfa.matches attempt: {0}'.format(i)

    def test_parse_regex(self):
        for i in range(100):
            ast = parse_regex('o|oa')
            assert ast.matches('o'), 'parse_regex attempt: {0}'.format(i)

    def test_nfa_from_ast(self):
        ast = parse_regex('o|oa')
        for i in range(100):
            nfa_ = nfa.from_ast(ast)
            assert nfa_.matches('o'), 'nfa.from_ast attempt: {0}'.format(i)

    def test_dfa_from_nfa(self):
        ast = parse_regex('o|oa')
        nfa_ = nfa.from_ast(ast)
        for i in range(100):
            dfa_ = dfa.from_nfa(nfa_)
            assert dfa_.matches('o'), 'dfa.from_nfa attempt: {0}'.format(i)

    def test_full_process(self):
        for i in range(100):
            ast = parse_regex('o|oa')
            nfa_ = nfa.from_ast(ast)
            dfa_ = dfa.from_nfa(nfa_)
            assert dfa_.matches('o'), 'full_process attempt: {0}'.format(i)
