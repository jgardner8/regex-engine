#!/usr/bin/env python3
import parser
import sys
import nfa
import dfa
from utils import constructor_str

if len(sys.argv) != 3:
    print('Usage: main.py "<regular expression>" "<string to match>"')
    sys.exit(1)
regex_str = sys.argv[1]
match_str = sys.argv[2]

print('InputRegex:  ' + regex_str)
ast = parser.parse_regex(regex_str)
print('ParsedRegex: ' + ast.to_regex())
print('AST: ' + constructor_str(ast))
print('English: ' + ast.to_str_english())
print('Full match (derivative): ' + str(ast.matches(match_str)))
nfa_ = nfa.from_ast(ast)
print('Full match (NFA): ' + str(nfa_.matches(match_str)))
dfa_ = dfa.from_nfa(nfa_)
print('Full match (DFA): ' + str(dfa_.matches(match_str)))
print('Subsets matched: ' + str(dfa_.find_subset_matches(match_str)))
