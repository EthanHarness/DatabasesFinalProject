from __future__ import annotations
from abc import ABC
from typing import List

from JsonParser.LexerTokens import Whitespace, Number, StringT, TrueValue, FalseValue, NullValue, \
    LBracket, RBracket, Comma, Colon, LBrace, RBrace
from JsonParser.JsonLexer import LexerToken, Token

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

class Parser:
    def __init__(self, lexerTokenization: List[LexerToken]) -> None:
        self.tokenization: List[LexerToken] = lexerTokenization
        self.locationInTokenization: int = 0 
    
    #Has side affect of incrementing location if we correctly match. 
    #We do this often on match so its fine.
    def matchToken(self, expectedTokenString: str) -> LexerToken:
        if self.getCurrentTokenString() != expectedTokenString:
            raise Exception("Failed to parse")
        
        #Only token where the token string and value are differnt 
        #This is due to the quotes surrounding strings so we remove them before we return
        if self.getCurrentTokenString() == StringT.TOKEN_STRING:
            newLexerValue: str = self.tokenization[self.locationInTokenization].value[1:-1]
            newLexerType: type[Token] = self.tokenization[self.locationInTokenization].type
            self.locationInTokenization += 1
            return LexerToken(newLexerValue, newLexerType)
        
        self.locationInTokenization += 1
        return self.tokenization[self.locationInTokenization - 1] 

    def matchIf(self, tokenStr: str) -> None:
        if self.getCurrentTokenString() == tokenStr:
            self.matchToken(tokenStr)
    
    #Parse Object,Array,Value (should) operate based on Json.org structure
    def ParseObject(self) -> List[ObjectConstruct]:
        objList: List[ObjectConstruct] = [] 
    
        self.matchToken(LBrace.TOKEN_STRING)
        self.matchIf(Whitespace.TOKEN_STRING)

        if self.getCurrentTokenString() == RBrace.TOKEN_STRING:
            self.matchToken(RBrace.TOKEN_STRING)
            return objList

        while(True):
            keyToken: LexerToken = self.matchToken(StringT.TOKEN_STRING)
            self.matchIf(Whitespace.TOKEN_STRING)
            self.matchToken(Colon.TOKEN_STRING)

            valueToken = self.ParseValue() #Will take care of leading and trailing white space
            objList.append(ObjectConstruct(keyToken, valueToken))

            if self.getCurrentTokenString() != Comma.TOKEN_STRING:
                break
            
            self.matchToken(Comma.TOKEN_STRING)
            self.matchIf(Whitespace.TOKEN_STRING)

        self.matchToken(RBrace.TOKEN_STRING)

        return objList

    def ParseArray(self) -> ArrayConstruct: 
        arrList: List[ValueConstruct] = []

        self.matchToken(LBracket.TOKEN_STRING)
        self.matchIf(Whitespace.TOKEN_STRING)
        self.matchIf(RBracket.TOKEN_STRING)

        while(True):
            arrList.append(self.ParseValue()) #Will take care of leading and trailing white space

            if self.getCurrentTokenString() != Comma.TOKEN_STRING:
                break
            
            self.matchToken(Comma.TOKEN_STRING)

        self.matchToken(RBracket.TOKEN_STRING)
        return ArrayConstruct(arrList)
        
    def ParseValue(self) -> ValueConstruct:
        val: LexerToken|None = None
        constructList: List[ParserConstruct]|None = None

        self.matchIf(Whitespace.TOKEN_STRING)
        match self.getCurrentTokenString():
            case StringT.TOKEN_STRING: val = self.matchToken(StringT.TOKEN_STRING)
            case Number.TOKEN_STRING: val = self.matchToken(Number.TOKEN_STRING)
            case TrueValue.TOKEN_STRING: val = self.matchToken(TrueValue.TOKEN_STRING)
            case FalseValue.TOKEN_STRING: val = self.matchToken(FalseValue.TOKEN_STRING)
            case NullValue.TOKEN_STRING: val = self.matchToken(NullValue.TOKEN_STRING)

            case _:
                try:
                    constructList = self.ParseObject()
                except: #If object fails then try array. If array fails then we should throw error anyways. 
                    #TODO: This is incorrect with existing type hints. 
                    #Parse Array returns just an ArrayConstruct not a List[ArrayConstruct]
                    #Either modify type hints or wrap in list. 
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
    
    def getCurrentTokenString(self, locationOffset: int = 0) -> str:
        return self.tokenization[self.locationInTokenization + locationOffset].type.TOKEN_STRING