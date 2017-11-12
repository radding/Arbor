import unittest

from src.lexer import lex, lexer, LexerError

class LexerTest(unittest.TestCase):
    def test_ignore(self):
        '''Tests that these are ignored!'''
        string = " \t\n"
        toks = lex(string)
        self.assertEquals(len(toks), 0)
        pass

    def test_comments(self):
        '''tests that comments are ignored by the lexer'''
        string = '// This is a comment with key words. All of this will get ignored: if else done'
        toks = lex(string)
        self.assertEquals(len(toks), 0)
        string = '''/*
        this is a big comment block
        this will not fail
        if else done return const let int float char function */'''
        oks = lex(string)
        self.assertEquals(len(toks), 0)
        pass

    def reserved(self, word, typ=None):
        typ = typ if typ is not None else word.upper()
        toks = lex(word)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, typ)
        self.assertEquals(toks[0].value, word)
        pass

    def test_reserved(self):
        '''tests that reserved keywords work'''
        self.reserved("if")
        self.reserved("else")
        self.reserved("done")
        self.reserved("return")
        self.reserved("const")
        self.reserved("let")
        self.reserved("int", "INTTYPE")
        self.reserved("float", "FLOATTYPE")
        self.reserved("char", "CHARTYPE")
        self.reserved("function", "FUNCTIONTYPE")
        st = "if else done return const let int float char function"
        tokenTypes = ["IF", "ELSE", "DONE", "RETURN", "CONST", "LET", "INTTYPE", "FLOATTYPE", "CHARTYPE", "FUNCTIONTYPE"]
        st_list = st.split()
        tokens = lex(st)
        self.assertEquals(len(tokens), 10)
        for ndx, i in enumerate(tokens):
            self.assertEquals(i.type, tokenTypes[ndx])
            self.assertEquals(i.value, st_list[ndx])
            pass
        pass

    def test_int(self):
        '''Tests that the lexer matches to int types'''
        integer = '1431'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "INT")
        self.assertEquals(toks[0].value, integer)

        integer = '11'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "INT")
        self.assertEquals(toks[0].value, integer)

        integer = '11.34'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertNotEquals(toks[0].type, "INT")

        integer = '011'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "OCT")
        self.assertEquals(toks[0].value, "9")

        integer = '0x11AeFF'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "HEX")
        self.assertEquals(toks[0].value, "1158911")

        integer = '-32111'
        toks = lex(integer)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "INT")
        self.assertEquals(toks[0].value, integer)

        integer = '11 123 55312 4391 2434'
        toks = lex(integer)
        self.assertEquals(len(toks), 5)
        for ndx, i in enumerate(toks):
            self.assertEquals(i.value, integer.split()[ndx])
            self.assertEquals(i.type, "INT")
            pass
        pass

    def test_float(self):
        '''tests that lexer matches flloating points!'''
        floats = '.33'
        toks = lex(floats)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "FLOAT")
        self.assertEquals(toks[0].value, floats)

        floats = '0.33'
        toks = lex(floats)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "FLOAT")
        self.assertEquals(toks[0].value, floats)

        floats = '-0.33'
        toks = lex(floats)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "FLOAT")
        self.assertEquals(toks[0].value, floats)
        pass

    def test_name(self):
        '''tests that names are discovered'''
        name = "this"
        toks = lex(name)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "NAME")
        self.assertEquals(toks[0].value, name)

        name = "yoseph"
        toks = lex(name)
        self.assertEquals(len(toks), 1)
        self.assertEquals(toks[0].type, "NAME")
        self.assertEquals(toks[0].value, name)

        name = '12tiemyshoe'
        def throwsException():
            toks = lex(name)
            pass
        self.assertRaises(LexerError, throwsException)
        pass

    def test_char(self):
        test = "'a'"
        toks = lex(test)
        self.assertEquals(toks[0].type, "CHAR")
        self.assertEquals(toks[0].value, "a")
        pass

    def test_string(self):
        test = '"abcdef"'
        toks = lex(test)
        self.assertEquals(toks[0].type, "STRING")
        self.assertEquals(toks[0].value, "abcdef")
        pass        

    def test_alltogethernow(self):
        code = '''
        const test = 1;
        let foo = (a, b, c) -> 
            if (a > b) -> 
                return c;
            else if (a < b) ->
                return b;
            else ->
                return a;
            done;
        '''
        
        
        expectedToks = [
            'CONST',
            'NAME',
            'EQ',
            'INT',
            'SEMICOLON',
            'LET',
            'NAME',
            'EQ',
            'LPAREN',
            'NAME',
            'COMMA',
            'NAME',
            'COMMA',
            'NAME', 
            'RPAREN',
            'ARROW',
            'IF',
            'LPAREN',
            'NAME',
            'GT',
            'NAME',
            'RPAREN',
            'ARROW',
            'RETURN',
            'NAME',
            'SEMICOLON',
            'ELSE',
            'IF',
            'LPAREN',
            'NAME',
            'LT',
            'NAME',
            'RPAREN',
            'ARROW',
            'RETURN',
            'NAME',
            'SEMICOLON',
            'ELSE',
            'ARROW',
            'RETURN',
            'NAME',
            'SEMICOLON',
            'DONE',
            'SEMICOLON',
        ]
        toks = lex(code)
        for ndx, i in enumerate(toks):
            self.assertEquals(expectedToks[ndx], i.type)
            pass
        pass
