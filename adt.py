'''Abstract data types (adt) to represent a regular expression as an abstract syntax tree (ast)'''
from abc import ABC, abstractmethod
from utils import SingletonMixin, ValueEqualityMixin, raise_if_not

class Regex(ABC, ValueEqualityMixin):
    @abstractmethod
    def matches_empty_str(self):
        '''Returns Epsilon() if this Regex matches an empty string, otherwise returns NullRegex()'''
        pass

    @abstractmethod
    def derivative(self, char):
        '''The derivative of a regular expression with respect to a character is a regular expression that 
        matches what the original expression would've matched, assuming it had just matched the character.
        For example, the derivative of the expression (foo|frak)* with respect to the character f is the 
        expression (oo|rak)(foo|frak)*.'''
        pass
    
    @abstractmethod
    def to_str_english(self): 
        '''Convert to an english sentence'''
        pass

    @abstractmethod
    def to_regex(self):
        '''Convert to a regular expression'''
        pass

    def matches(self, s):
        if s:
            return self.derivative(s[0]).matches(s[1:])
        return self.matches_empty_str() == Epsilon()

class Or(Regex):
    def __new__(cls, regex_a, regex_b):
        if regex_a == NullRegex():
            return regex_b
        if regex_b == NullRegex():
            return regex_a
        if regex_a == regex_b:
            return regex_a

        self = super().__new__(cls)
        self.regex_a = regex_a
        self.regex_b = regex_b
        return self      

    def matches_empty_str(self):
        '''δ(re1 | re2) = δ(re1) | δ(re2)'''
        return Or(self.regex_a.matches_empty_str(), self.regex_b.matches_empty_str())

    def derivative(self, char):
        '''Dc(re1 | re2) = Dc(re1) | Dc(re2)'''
        return Or(self.regex_a.derivative(char), self.regex_b.derivative(char))

    def to_str_english(self):
        return '{0} or {1}'.format(self.regex_a.to_str_english(), self.regex_b.to_str_english())

    def to_regex(self):
        if self.regex_a in _do_not_need_brackets and self.regex_b in _do_not_need_brackets:
            return '{0}|{1}'.format(self.regex_a.to_regex(), self.regex_b.to_regex())     
        return '({0}|{1})'.format(self.regex_a.to_regex(), self.regex_b.to_regex())        

class Sequence(Regex):
    def __new__(cls, regex_a, regex_b):
        if NullRegex() in (regex_a, regex_b):
            return NullRegex()
        if regex_a == Epsilon():
            return regex_b
        if regex_b == Epsilon():
            return regex_a

        self = super().__new__(cls)
        self.regex_a = regex_a
        self.regex_b = regex_b    
        return self      

    def matches_empty_str(self):
        '''δ(re1 re2) = δ(re1) δ(re2)'''
        return Sequence(self.regex_a.matches_empty_str(), self.regex_b.matches_empty_str())

    def derivative(self, char):
        '''Dc(re1 re2) = δ(re1) Dc(re2) | Dc(re1) re2'''
        return Or(
            Sequence(self.regex_a.matches_empty_str(), self.regex_b.derivative(char)),
            Sequence(self.regex_a.derivative(char), self.regex_b)
        )

    def to_str_english(self):
        # If Sequence(a, ZeroOrMore(a)), which is aa*, convert to a+
        if type(self.regex_b) == ZeroOrMore and self.regex_a == self.regex_b.regex:
            return self.regex_b.to_str_english().replace('any number of', 'one or more')
        return '{0}, {1}'.format(self.regex_a.to_str_english(), self.regex_b.to_str_english())

    def to_regex(self):
        # If Sequence(a, ZeroOrMore(a)), which is aa*, convert to a+
        if type(self.regex_b) == ZeroOrMore and self.regex_a == self.regex_b.regex:
            return self.regex_b.to_regex()[:-1] + '+'
        return self.regex_a.to_regex() + self.regex_b.to_regex()

class ZeroOrMore(Regex):
    def __new__(cls, regex):
        if regex in (NullRegex(), Epsilon()):
            return Epsilon()
        if type(regex) == ZeroOrMore:
            return regex
        if type(regex) == Optional:
            regex = regex.regex

        self = super().__new__(cls)
        self.regex = regex
        return self      

    def matches_empty_str(self):
        '''δ(re*) = ε'''
        return Epsilon()

    def derivative(self, char):
        '''Dc(re*) = Dc(re) re*'''
        return Sequence(self.regex.derivative(char), self)

    def to_str_english(self):
        return '({0} any number of times)'.format(self.regex.to_str_english())

    def to_regex(self):
        if type(self.regex) in _do_not_need_brackets:
            return '{0}*'.format(self.regex.to_regex())
        return '({0})*'.format(self.regex.to_regex())

class Optional(Regex):
    def __new__(cls, regex):
        if regex in (NullRegex(), Epsilon()):
            return Epsilon()
        if type(regex) == Optional:
            return regex
        if type(regex) == ZeroOrMore:
            return regex

        self = super().__new__(cls)
        self.regex = regex
        return self    

    def matches_empty_str(self):
        '''δ(re?) = ε'''
        return Epsilon()

    def derivative(self, char):
        '''Dc(re?) = Dc(re)'''
        return self.regex.derivative(char)

    def to_str_english(self):
        return '(optional {0})'.format(self.regex.to_str_english())

    def to_regex(self):
        if type(self.regex) in _do_not_need_brackets:
            return '{0}?'.format(self.regex.to_regex())
        return '({0})?'.format(self.regex.to_regex())        

class Char(Regex):
    def __init__(self, char):
        raise_if_not(len(char) == 1, 'char must be a string of length 1, got: {0}'.format(char))
        self.char = char

    def matches_empty_str(self):
        '''δ(c) = ∅'''
        return NullRegex()

    def derivative(self, char):
        '''
        Dc(c) = ε
        Dc(c') = ∅ if c ≠ c'
        '''
        return Epsilon() if char == self.char else NullRegex()

    def to_str_english(self):
        return self.char

    def to_regex(self):
        if self.char in ('(', ')', '\\', '.', '|', '*', '+', '[', ']'):
            return '\{0}'.format(self.char)
        return self.char

class AnyChar(Regex, SingletonMixin):
    def matches_empty_str(self):
        '''δ(c) = ∅'''
        return NullRegex()

    def derivative(self, char):
        '''Dc(c) = ε'''
        return Epsilon()

    def to_str_english(self):
        return 'any character'

    def to_regex(self):
        return '.'

class CharClass(Regex):
    def __new__(cls, invert, strs_or_char_ranges):
        raise_if_not(all((type(str_or_char_range) == str and len(str_or_char_range) == 1) or 
            (type(str_or_char_range) == CharRange) for str_or_char_range in strs_or_char_ranges),
            'strs_or_char_ranges must be a list of strings with length 1 and CharRange objects')

        if len(strs_or_char_ranges) == 1 and type(strs_or_char_ranges[0]) == str and not invert:
            return Char(strs_or_char_ranges[0])

        self = super().__new__(cls)
        self.strs_or_char_ranges = strs_or_char_ranges
        self.invert = invert
        return self

    def matches_empty_str(self):
        '''δ(c) = ∅'''
        return NullRegex()

    def derivative(self, char):
        '''
        Dc(c) = ε
        Dc(c') = ∅ if c' not in strs_or_char_ranges
        invert option swaps ε for ∅ after evaluation
        '''
        derivative = Epsilon() if any(char in str_or_char_range for str_or_char_range in self.strs_or_char_ranges) else NullRegex()
        if self.invert:
            return Epsilon() if derivative == NullRegex() else NullRegex()
        return derivative

    def _chars_str(self):
        return [str_or_char_range.to_regex() if type(str_or_char_range) == CharRange else str(str_or_char_range) 
            for str_or_char_range in self.strs_or_char_ranges]

    def to_str_english(self):
        return '{0}in {1}'.format('not ' if self.invert else '', self._chars_str())

    def to_regex(self):
        chars_str = self._chars_str()
        for i in range(0, len(chars_str)):
            if chars_str[i] in ('\\', ']'):
                chars_str[i] = '\{0}'.format(chars_str[i])
        # Only need to escape dashes (-) if not the first or last character of character class
        for i in range(1, len(chars_str)-1):
            if chars_str[i] == '-':
                chars_str[i] = '\-'
        return '[{0}{1}]'.format('^' if self.invert else '', ''.join(chars_str))

class CharRange:
    def __init__(self, start, end):
        raise_if_not(start < end, 'Invalid CharRange, start >= end ({0} >= {1})'.format(start, end))
        self.start = start
        self.end = end
        self.__iter__()

    def __iter__(self):
        self.cur_idx = ord(self.start)
        self.end_idx = ord(self.end)+1
        return self

    def __next__(self):
        if self.cur_idx >= self.end_idx:
            raise StopIteration()
        char = chr(self.cur_idx)
        self.cur_idx += 1
        return char

    def __contains__(self, char):
        return self.start <= char <= self.end

    def to_regex(self):
        return '{0}-{1}'.format(self.start, self.end)

    def __eq__(self, other):
        return type(other) == CharRange and self.start == other.start and self.end == other.end

class Epsilon(Regex, SingletonMixin):
    '''Represents a value matchable with no input'''
    def matches_empty_str(self):
        '''δ(ε) = ε'''
        return self

    def derivative(self, char):
        '''Dc(ε) = ∅'''
        return NullRegex()

    def to_str_english(self):
        return ''

    def to_regex(self):
        return ''

class NullRegex(Regex, SingletonMixin):
    '''Represents a pattern that is impossible to match'''
    def matches_empty_str(self):
        '''δ(∅) = ∅'''
        return self

    def derivative(self, char):
        '''Dc(∅) = ∅'''
        return self

    def to_str_english(self):
        return '∅'

    def to_regex(self):
        raise ValueError('NullRegex.to_regex()')


_do_not_need_brackets = (CharClass, Char, AnyChar)
