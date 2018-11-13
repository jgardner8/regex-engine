import unittest
import generators
import nfa
import dfa
from parser import parse_regex
from utils import constructor_str

PRINT_TESTS = False

class TestRandomlyGenerated(unittest.TestCase):
    '''Tests based completely on randomly-generated data'''
    def test_matching_str(self):
        REGEX_TO_TEST = 25
        MATCHING_STR_TO_TEST = 100

        for _ in range(REGEX_TO_TEST):
            ast = generators.ast()
            nfa_ = nfa.from_ast(ast)
            dfa_ = dfa.from_nfa(nfa_)
            
            if PRINT_TESTS:
                print('-----TEST: matching_str-----')
            for _ in range(MATCHING_STR_TO_TEST):
                matching_str = generators.matching_str(ast)
                if PRINT_TESTS:
                    print(ast.to_regex() + ' against ' + matching_str)
                self.assertTrue(ast.matches(matching_str), "Regex: '{0}' and String: '{1}' ".format(ast.to_regex(), matching_str) +
                    "were generated as a matching pair, but they were determined not to match by the derivative method.")

                self.assertTrue(nfa_.matches(matching_str), "Regex: '{0}' and String: '{1}' ".format(ast.to_regex(), matching_str) +
                    "were generated as a matching pair, but they were determined not to match by the NFA method.")

                self.assertTrue(dfa_.matches(matching_str), "Regex: '{0}' and String: '{1}' ".format(ast.to_regex(), matching_str) +
                    "were generated as a matching pair, but they were determined not to match by the DFA method.")

    def test_to_regex(self):
        REGEX_TO_TEST = 1000

        if PRINT_TESTS:
            print('-----TEST: parse_regex, to_regex-----')
        for _ in range(REGEX_TO_TEST):
            ast = generators.ast()
            regex = ast.to_regex()  
            try:
                # Can't test regex itself because the first parse will make optimisations
                regex_round_trip = parse_regex(regex).to_regex()
                regex_double_round_trip = parse_regex(regex_round_trip).to_regex()
            except:
                # Keep in mind it could have failed on the first or second round trip
                print("Can't parse: " + regex)
                print('Came from ast: ' + constructor_str(ast))
                raise

            if PRINT_TESTS:
                print(regex_round_trip + ' against ' + regex_double_round_trip)
            self.assertEqual(regex_round_trip, regex_double_round_trip)