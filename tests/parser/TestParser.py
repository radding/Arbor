import unittest

from src.parser import parse, ParserError

class ParserTest(unittest.TestCase):

    def test_statements(self):
        parseRes = parse("", True)
        self.assertEquals(parseRes, ["statements", []])
        pass

    def test_constants(self):
        string = '123; 1.045;'
        parseRes = parse(string)
        self.assertEquals(parseRes, ["statements", [["int", "123"], ["float", "1.045"]]])
        pass

    def test_name(self):
        string = "test;"
        parseRes = parse(string)
        self.assertEquals(parseRes, ["statements", [["usage", "test"]]])
        pass
    
    def test_assignment(self):
        string = "test = a;"
        parseRes = parse(string)
        self.assertEquals(parseRes, [
            "statements",
            [
                ["assign",
                    ["usage", "test"],
                    ["usage", "a"]
                ]
            ]
        ])
        pass
    
    def test_binop(self):
        string = "1 + 3;"
        parseRes = parse(string)
        self.assertEquals([
            "statements",
            [
                ["binop",
                    ["int", "1"],
                    "+",
                    ["int", "3"]
                ]
            ]
        ], parseRes)
        string = "1 - 3;"
        parseRes = parse(string)
        self.assertEquals([
            "statements",
            [
                ["binop",
                    ["int", "1"],
                    "-",
                    ["int", "3"]
                ]
            ]
        ], parseRes)

        string = "1 * 3;"
        parseRes = parse(string)
        self.assertEquals([
            "statements",
            [
                ["binop",
                    ["int", "1"],
                    "*",
                    ["int", "3"]
                ]
            ]
        ], parseRes)

        string = "1 * 3;"
        parseRes = parse(string)
        self.assertEquals([
            "statements",
            [
                ["binop",
                    ["int", "1"],
                    "*",
                    ["int", "3"]
                ]
            ]
        ], parseRes)
        pass

    def test_decl(self):
        string = "let test;"
        parseRes = parse(string)
        self.assertEquals([
            "statements", 
            [
                ["decl", "test"]
            ]
        ], parseRes)

        string = "const test;"
        parseRes = parse(string)
        self.assertEquals([
            "statements", 
            [
                ["declConst", "test"]
            ]
        ], parseRes)
        pass

    def test_bigFunctionDef(self):
        string = '''
        (a, b, c) -> 
            a = a + 1;
            b = b + a;
        done;'''
        parser = parse(string)

        self.assertEquals([
            'statements', [
                ['func', [
                    'params', [
                        ['param', 'c'], 
                        ['param', 'b'], 
                        ['param', 'a']
                    ]
                ], [
                    'block', [
                        ['assign', 
                            ['usage', 'a'], 
                            ['binop', 
                                ['usage', 'a'], '+', 
                                ['int', '1']
                            ]
                        ], 
                        ['assign', 
                            ['usage', 'b'], 
                            ['binop', 
                                ['usage', 'b'], '+', 
                                ['usage', 'a']
                            ]
                        ]
                    ]
                ]
            ]
        ]], parser)
        pass

    def test_bigFunctionDefWithType(self):
        string = '''
        (a:int, b:float, c:char, d:function) -> 
            a = a + 1;
            b = b + a;
        done;'''
        parser = parse(string)

        self.assertEquals([
            'statements', [
                ['func', [
                    'params', [
                        ['paramtype', 'd', 'function'], 
                        ['paramtype', 'c', 'char'], 
                        ['paramtype', 'b', 'float'], 
                        ['paramtype', 'a', 'int']
                    ]
                ], [
                    'block', [
                        ['assign', 
                            ['usage', 'a'], 
                            ['binop', 
                                ['usage', 'a'], '+', 
                                ['int', '1']
                            ]
                        ], 
                        ['assign', 
                            ['usage', 'b'], 
                            ['binop', 
                                ['usage', 'b'], '+', 
                                ['usage', 'a']
                            ]
                        ]
                    ]
                ]
            ]
        ]], parser)
        pass

    def test_bigFunctionDefWithTypeAndDefault(self):
        string = '''
        (c:char, d:function, a:int = 1, b:float = .2) -> 
            a = a + 1;
            b = b + a;
        done;'''
        parser = parse(string)
        
        self.assertEquals([
            'statements', [
                ['func', [
                    'params', [
                        ["default", ['paramtype', 'b', 'float'], ['float', '.2']], 
                        ['default', ['paramtype', 'a', 'int'], ['int', '1']],
                        ['paramtype', 'd', 'function'], 
                        ['paramtype', 'c', 'char'], 
                    ]
                ], [
                    'block', [
                        ['assign', 
                            ['usage', 'a'], 
                            ['binop', 
                                ['usage', 'a'], '+', 
                                ['int', '1']
                            ]
                        ], 
                        ['assign', 
                            ['usage', 'b'], 
                            ['binop', 
                                ['usage', 'b'], '+', 
                                ['usage', 'a']
                            ]
                        ]
                    ]
                ]
            ]
        ]], parser)
        pass

    def test_functionNoParams(self):
        string = '''
        () -> 
            a = a + 1;
            b = b + a;
        done;'''
        parser = parse(string)
        
        self.assertEquals([
            'statements', [
                ['func', None, [
                    'block', [
                        ['assign', 
                            ['usage', 'a'], 
                            ['binop', 
                                ['usage', 'a'], '+', 
                                ['int', '1']
                            ]
                        ], 
                        ['assign', 
                            ['usage', 'b'], 
                            ['binop', 
                                ['usage', 'b'], '+', 
                                ['usage', 'a']
                            ]
                        ]
                    ]
                ]
            ]
        ]], parser)
        pass

    def test_parserFails(self):
        string = '''
        () -> 
            a + b;
        '''
        self.assertRaises(ParserError, parse, string, True)
        pass

    def test_parserFailsWithPDefined(self):
        string = '''
        let name === 1;
        '''
        self.assertRaises(ParserError, parse, string, True)
        pass

    def test_if(self):
        string = '''
        if (a) ->
            a;
        done;
        '''
        parser = parse(string, True)
        self.assertEquals([
            'statements', [
                ['if', [
                    'usage', 'a'
                ], 
                [
                    ['usage', 'a']
                ]
            ]
        ]], parser)
        pass