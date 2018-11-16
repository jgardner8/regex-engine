A regular expression engine created for learning purposes. Could serve as a good reference for how a regular expression engine works.

Uses a recursive descent parser to create an AST. 
Has three evaluation methods:
* Derivatives
* Non-deterministic finite automata (NFA)
* Deterministic finite automata (DFA)

Usage:
`python main.py "<regular expression>" "<string to match>"`

Examples:
```
$ python main.py "a+b" aaaab
InputRegex:  a+b
ParsedRegex: a+b
AST: Sequence(Sequence(Char('a'), ZeroOrMore(Char('a'))), Char('b'))
English: (a one or more times), b
Full match (derivative): True
Full match (NFA): True
Full match (DFA): True
Subsets matched: ['aaaab']
```

```
$ python main.py "\w+@\w+\.\w+" "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean vel sem augue. Vestibulum pulvinar est mauris, ut viverra arcu maximus at. Duis@iaculis.turpis eu dui vestibulum feugiat. Etiam feugiat tincidunt augue, vitae sollicitudin ante maximus quis. In hac habitasse platea dictumst. Aliquam vel magna@leo.Donec ullamcorper sapien eget consectetur dictum. Donec@felis.nisi, pulvinar id dui vitae, mattis rhoncus nibh. Maecenas ac metus sapien."
InputRegex:  \w+@\w+\.\w+
ParsedRegex: [A-Za-z0-9_]+@[A-Za-z0-9_]+\.[A-Za-z0-9_]+
AST: Sequence(Sequence(Sequence(Sequence(Sequence(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_']), ZeroOrMore(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_']))), Char('@')), Sequence(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_']), ZeroOrMore(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_'])))), Char('.')), Sequence(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_']), ZeroOrMore(CharClass(False, [CharRange('A', 'Z'), CharRange('a', 'z'), CharRange('0', '9'), '_']))))
English: (in ['A-Z', 'a-z', '0-9', '_'] one or more times), @, (in ['A-Z', 'a-z', '0-9', '_'] one or more times), ., (in ['A-Z', 'a-z', '0-9', '_'] one or more times)
Full match (derivative): False
Full match (NFA): False
Full match (DFA): False
Subsets matched: ['Duis@iaculis.turpis', 'magna@leo.Donec', 'Donec@felis.nisi']
```