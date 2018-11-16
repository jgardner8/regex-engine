import adt
import adt_fancy_constructors

def parse_regex(input_str):
    return _RegexParser(input_str).parse()

class _RegexParser:
    '''Recursive descent parser to construct an AST of type Regex from a regular expression string'''
    #
    # Interface
    #
    def __init__(self, input_str):
        self.input_str = input_str
        self.input_index = 0 # current position in input_str

    def parse(self):
        ast = self._regex()
        self.input_index = 0 # reset state
        return ast

    #
    # Recursive descent parsing internals
    #
    def _peek(self):
        '''Returns the next item of input_str without consuming it'''
        return self.input_str[self.input_index];

    def _eat(self, char):
        '''Consumes the next char of input_str, failing if not equal to char'''
        assert self._peek() == char, 'Expected: {0}, got: {1}, at position: {2}'.format(
            char, self._peek(), self.input_index)
        self.input_index += 1

    def _next(self):
        '''Returns the next item of input_str and consumes it'''
        char = self._peek()
        self._eat(char)
        return char

    def _more(self):
        '''Returns true if input_str still has more input to consume'''
        return self.input_index < len(self.input_str)

    #
    # Context-free grammar types
    #
    def _regex(self):
        '''
        <regex> ::= <term> [ '|' <regex> ]
        '''
        term = self._term()

        if self._more() and self._peek() == '|':
            self._eat('|')
            regex = self._regex()
            return adt.Or(term, regex)
        return term

    def _term(self):
        '''<term> ::= { <factor> }'''
        factors = []
        while self._more() and self._peek() not in (')', '|'):
            factors.append(self._factor())

        if len(factors) == 0:
            return adt.Epsilon()
        elif len(factors) == 1:
            return factors[0]
        return adt_fancy_constructors.sequence_tree_from_regexes(factors)

    def _factor(self):
        '''<factor> ::= <base> { '*' | '+' | '?' | '{' <quantifier> '}' }'''
        base = self._base()
 
        while self._more() and self._peek() in ('*', '+', '?', '{'):
            char = self._next()
            if char == '*':
                base = adt.ZeroOrMore(base)
            elif char == '+':
                base = adt.Sequence(base, adt.ZeroOrMore(base)) # a+ = aa*
            elif char == '?':
                base = adt.Optional(base)
            elif char == '{':
                base = self._quantifier(base)
                self._eat('}')
            else:
                raise ValueError('Expected: *, + or ?, got: {0}, at position'.format(char, self.input_index))

        return base

    def _base(self):
        '''
        <base> ::= '.'
                |  '\' <backslash-char>
                |  '(' <regex> ')'  
                |  '[' <char-class> ']'
                |  <char>
        '''
        char = self._next()

        if char == '(':
            regex = self._regex()
            self._eat(')')
            return regex
        elif char == '[':
            char_class = self._char_class()
            self._eat(']')
            return char_class
        elif char == '.':
            return adt.AnyChar()
        elif char == '\\':
            return self._backslash_char()
        return adt.Char(char)

    def _quantifier(self, regex):
        '''
        <quantifier> ::= <int> [ ',' [ <int> ] ]
        '''
        lower_bound = self._int()
        repeated = [regex] * lower_bound # a{3} = aaa

        if self._peek() != '}':
            self._eat(',')
            if self._peek() == '}':
                repeated.append(adt.ZeroOrMore(regex)) # a{3,} = aaaa*
            else:
                upper_bound = self._int()
                repeated.extend([adt.Optional(regex)] * (upper_bound-lower_bound)) # a{3,5} = aaaa?a?

        return adt_fancy_constructors.sequence_tree_from_regexes(repeated)

    def _int(self):
        ''' [0-9]+ '''
        digits = [self._next()]
        while self._more() and str.isdigit(self._peek()):
            digits.append(self._next())
        return int(''.join(digits))

    def _backslash_char(self):
        '''
        <backslash-char> ::= '\' <char-class-shorthand>
                          |  '\' <escaped-char>
        '''
        char = self._next()

        if str.lower(char) in ('d', 's', 'w'): # char class shorthand
            if str.lower(char) == 'd':
                char_class = adt.CharClass(invert=False, strs_or_char_ranges=[adt.CharRange('0', '9')])
            elif str.lower(char) == 's':
                char_class = adt.CharClass(invert=False, strs_or_char_ranges=[' ', '\t', '\r', '\n', '\f'])
            elif str.lower(char) == 'w':
                char_class = adt.CharClass(invert=False, strs_or_char_ranges=[
                    adt.CharRange('A', 'Z'), adt.CharRange('a', 'z'), adt.CharRange('0', '9'), '_'])
            else:
                raise ValueError('Expected d, s or w, got: {0}'.format(char))

            if str.isupper(char):
                char_class.invert = True
            return char_class
        return adt.Char(char) # escaped char

    def _char_class(self):
        '''<char-class> ::= [ '^' ] { <char> '-' <char> | '\' <char> | <char> }'''
        if self._peek() == '^':
            invert = True
            self._eat('^')
        else:
            invert = False

        chars = []
        while self._more() and self._peek() != ']':
            char = self._next()
            if char == '\\':
                char = self._next() # escaped
                    
            if self._peek() == '-':
                self._eat('-')
                if self._peek() == ']': # they want a dash (-), not a range
                    chars.append(char)
                    chars.append('-')
                else:
                    chars.append(adt.CharRange(start=char, end=self._next()))
            else:
                chars.append(char)

        return adt.CharClass(invert, chars)
