from __future__ import annotations
from abc import ABC
from typing import List

from JsonParser.LexerTokens import Whitespace, Number, StringT, TrueValue, FalseValue, NullValue, \
    LBracket, RBracket, Comma, Colon, LBrace, RBrace
from JsonParser.JsonLexer import Lexer, LexerToken

class ParserConstruct(ABC):
    pass
        
class ObjectConstruct(ParserConstruct):
    def __init__(self, keyLexer: LexerToken, valueConstruct: ParserConstruct):
        self.keyValue: str = keyLexer.value
        self.keyType: str = keyLexer.type
        self.value: ParserConstruct = valueConstruct

class ValueConstruct(ParserConstruct):
    def __init__(self, value: List[ParserConstruct]|LexerToken, type):
        self.value: List[ParserConstruct]|LexerToken = value
        self.type = type #0 if parserConstruct 1 if lexer tken

class ArrayConstruct(ParserConstruct):
    def __init__(self, arrayValueList: List[ParserConstruct]):
        self.value: List[ParserConstruct]  = arrayValueList
        self.length: int = len(arrayValueList)

class ParsedJson:
    def __init__(self, document: List[ObjectConstruct]):
        self.document = document
        self.pythonDoc = {}
        
        self.createDocument()
    
    @staticmethod
    def recursivelyCreateDocument(val: ParserConstruct):
        if isinstance(val, ObjectConstruct):
            res = {}
            res[val.keyValue] = ParsedJson.recursivelyCreateDocument(val.value)
            return res
        
        if isinstance(val, ArrayConstruct):
            res = []
            for x in val.value:
                res.append(ParsedJson.recursivelyCreateDocument(x))
            return res
            
        assert isinstance(val, ValueConstruct), "Somehow got a non value construct here. Fix."
        if val.type == 0:
            assert isinstance(val.value, LexerToken), "Somehow got non lexer token value here. Fix."
            return val.value.getCastedValue()
        
        if isinstance(val.value, ArrayConstruct): return ParsedJson.recursivelyCreateDocument(val.value)

        assert isinstance(val.value, List), "Somehow got non list type here. Fix."
        res = {}
        for x in val.value:
            assert isinstance(x, ObjectConstruct), "Somehow got non object here. Fix."
            res[x.keyValue] = ParsedJson.recursivelyCreateDocument(x.value)
        return res

    def createDocument(self):
        for x in self.document:
            self.pythonDoc[x.keyValue] = ParsedJson.recursivelyCreateDocument(x.value)

    def printDocument(self):
        for index,x in enumerate(self.document):
            pStr = self.recursivePrintValue(x, 0)
            if index != len(self.document) - 1: print(f"{pStr[0:-1]},")
            else: print(pStr)

    @staticmethod
    def recursivePrintValue(val: ParserConstruct, tabLevel=0) -> str:
        tabString: str = "\t" * tabLevel
        resStr: str = ""
        if isinstance(val, ObjectConstruct):
            resStr += f"{tabString}{{\n{tabString}\t{val.keyValue}:"
            resStr += f"{ParsedJson.recursivePrintValue(val.value, tabLevel)}{tabString}}}\n"
            return resStr
        
        if isinstance(val, ArrayConstruct):
            resStr += f"\n{tabString}["
            for x in val.value:
                resStr += f"\n{tabString}\t\t {ParsedJson.recursivePrintValue(x, tabLevel+2)[0:-1]},"
            resStr += f"\n{tabString}]\n"
            return resStr

        assert isinstance(val, ValueConstruct), "Somehow got a non value construct here. Fix."
        if val.type == 0:
            assert isinstance(val.value, LexerToken), "Somehow got non lexer token value here. Fix."
            resStr += f"{val.value.value}\n"
            return resStr

        if isinstance(val.value, ArrayConstruct): 
            resStr += ParsedJson.recursivePrintValue(val.value, tabLevel+2)
            return resStr
        
        assert isinstance(val.value, List), "Somehow got non list type here. Fix."
        for x in val.value: 
            resStr += "\n"
            resStr += ParsedJson.recursivePrintValue(x, tabLevel+2)
        return resStr

class Parser:
    def __init__(self, lexerTokenization: List[LexerToken]) -> None:
        self.tokenization: List[LexerToken] = lexerTokenization
        self.locationInTokenization: int = 0 
    
    def matchToken(self, expectedTokenString: str) -> LexerToken:
        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING != expectedTokenString:
            raise Exception("Failed to parse")
        self.locationInTokenization += 1
        if self.tokenization[self.locationInTokenization - 1].type.TOKEN_STRING == StringT.TOKEN_STRING:
            return LexerToken(self.tokenization[self.locationInTokenization - 1].value[1:-1], self.tokenization[self.locationInTokenization - 1].type)
        return self.tokenization[self.locationInTokenization - 1] 

    def matchIf(self, tokenStr: str) -> None:
        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == tokenStr:
            self.matchToken(tokenStr)
        
    def ParseObject(self) -> List[ObjectConstruct]:
        objList: List[ObjectConstruct] = []
        startTokenIndex = self.locationInTokenization 
    
        self.matchToken(LBrace.TOKEN_STRING)
        self.matchIf(Whitespace.TOKEN_STRING)

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == RBrace.TOKEN_STRING:
            self.matchToken(RBrace.TOKEN_STRING)
            return objList

        while(True):
            keyToken: LexerToken = self.matchToken(StringT.TOKEN_STRING)
            self.matchIf(Whitespace.TOKEN_STRING)
            self.matchToken(Colon.TOKEN_STRING)

            valueToken = self.ParseValue() #Will take care of leading and trailing white space
            objList.append(ObjectConstruct(keyToken, valueToken))

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING != Comma.TOKEN_STRING:
                break
            
            self.matchToken(Comma.TOKEN_STRING)
            self.matchIf(Whitespace.TOKEN_STRING)

        self.matchToken(RBrace.TOKEN_STRING)

        return objList

    def ParseArray(self) -> ArrayConstruct:
        startTokenIndex = self.locationInTokenization 
        arrList: List[ValueConstruct] = []

        self.matchToken(LBracket.TOKEN_STRING)
        self.matchIf(Whitespace.TOKEN_STRING)
        self.matchIf(RBracket.TOKEN_STRING)

        while(True):
            arrList.append(self.ParseValue()) #Will take care of leading and trailing white space

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING != Comma.TOKEN_STRING:
                break
            
            self.matchToken(Comma.TOKEN_STRING)

        self.matchToken(RBracket.TOKEN_STRING)
        return ArrayConstruct(arrList)
        
    def ParseValue(self) -> ValueConstruct:
        startTokenIndex = self.locationInTokenization
        val: LexerToken|None = None
        constructList: List[ParserConstruct]|None = None

        self.matchIf(Whitespace.TOKEN_STRING)
        match self.tokenization[self.locationInTokenization].type.TOKEN_STRING:
            case StringT.TOKEN_STRING: val = self.matchToken(StringT.TOKEN_STRING)
            case Number.TOKEN_STRING: val = self.matchToken(Number.TOKEN_STRING)
            case TrueValue.TOKEN_STRING: val = self.matchToken(TrueValue.TOKEN_STRING)
            case FalseValue.TOKEN_STRING: val = self.matchToken(FalseValue.TOKEN_STRING)
            case NullValue.TOKEN_STRING: val = self.matchToken(NullValue.TOKEN_STRING)

            case _:
                try:
                    constructList = self.ParseObject()
                except: #If object fails then try array. If array fails then we should throw error anyways. 
                    constructList = self.ParseArray()

        self.matchIf(Whitespace.TOKEN_STRING)

        if constructList != None: return ValueConstruct(constructList, 1)
        
        assert val != None, "Value is None type somehow. Fix this."
        return ValueConstruct(val, 0)

    def printLexerTokenRange(self, start: int, end: int) -> str:
        resStr: str = ""
        for x in range(start, end):
            resStr += self.tokenization[x].value
        return resStr
    
    def parseJson(self) -> ParsedJson:
        return ParsedJson(self.ParseObject())



def loadJson(filePath: str = "") -> dict:
    with open(filePath, newline='', mode="r") as file:
        stream: str = file.read()
        lexer: Lexer = Lexer(stream)
        lexer.scanStream()

        parser: Parser = Parser(lexer.streamTokenization)
    parsed = parser.parseJson()
    return parsed.pythonDoc


