import unittest
from utils import constructor_str

class InitClass:
    def __init__(self, a, b):
        self.a = a 
        self.b = b

class NewClass:
    def __new__(cls, a, b, c):
        self = super().__new__(cls)
        self.a = a 
        self.b = b
        self.c = c
        return self

class ArgsClass:
    def __init__(self, *args):
        self.a = args[0]
        self.b = args[1]

class TestConstructorStr(unittest.TestCase):
    def test_constructor_str(self):
        value   =  InitClass(('1', None, True, 3.4), '2')
        desired = "InitClass(('1', None, True, 3.4), '2')"
        self.assertEqual(constructor_str(value), desired)

        value   =  NewClass(1, InitClass(1, '2'), [1, 2, '3'])
        desired = "NewClass(1, InitClass(1, '2'), [1, 2, '3'])"
        self.assertEqual(constructor_str(value), desired)

        value   =  NewClass(1, [InitClass(1, '2'), 1], (InitClass('1', False), True))
        desired = "NewClass(1, [InitClass(1, '2'), 1], (InitClass('1', False), True))"
        self.assertEqual(constructor_str(value), desired)

        with self.assertRaises(ValueError):
            constructor_str(ArgsClass(1, 2))