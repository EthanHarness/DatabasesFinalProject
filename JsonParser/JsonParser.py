from typing import List

from LexerTokens import Whitespace, Number, StringT, TrueValue, FalseValue, NullValue, \
    LBracket, RBracket, Comma, Colon, LBrace, RBrace
from JsonLexer import Lexer, LexerToken

#May need later when we need to get values off objects and such
"""class ParserConstruct:
    def __init__(self, tokens: List[LexerToken]):
        self.tokens = tokens"""

class Parser:
    def __init__(self, lexerTokenization: List[LexerToken]) -> None:
        self.tokenization: List[LexerToken] = lexerTokenization
        self.locationInTokenization: int = 0 
    
    def matchToken(self, expectedTokenString: str, token: LexerToken) -> None:
        if token.type.TOKEN_STRING != expectedTokenString:
            raise Exception("Failed to parse")
        
    def ParseObject(self) -> None:
        startTokenIndex = self.locationInTokenization 

        self.matchToken(LBrace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
        self.locationInTokenization += 1

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
            self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == RBrace.TOKEN_STRING:
            self.matchToken(RBrace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1
            return

        while(True):
            self.matchToken(StringT.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
                self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            self.matchToken(Colon.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

            self.ParseValue() #Will take care of leading and trailing white space

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING != Comma.TOKEN_STRING:
                break

            self.matchToken(Comma.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
                self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

        self.matchToken(RBrace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
        self.locationInTokenization += 1

        print(f"Object has tokens from index {startTokenIndex} to index {self.locationInTokenization-1}")
        if self.locationInTokenization == len(self.tokenization):
            return

    def ParseArray(self) -> None:
        startTokenIndex = self.locationInTokenization 

        self.matchToken(LBracket.TOKEN_STRING, self.tokenization[self.locationInTokenization])
        self.locationInTokenization += 1

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
            self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == RBracket.TOKEN_STRING:
            self.matchToken(RBracket.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        while(True):
            self.ParseValue() #Will take care of leading and trailing white space

            if self.tokenization[self.locationInTokenization].type.TOKEN_STRING != Comma.TOKEN_STRING:
                break

            self.matchToken(Comma.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        self.matchToken(RBracket.TOKEN_STRING, self.tokenization[self.locationInTokenization])
        self.locationInTokenization += 1

        print(f"Array has tokens from index {startTokenIndex} to index {self.locationInTokenization-1}")
        
    def ParseValue(self) -> None:
        startTokenIndex = self.locationInTokenization

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
            self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        match self.tokenization[self.locationInTokenization].type.TOKEN_STRING:

            case StringT.TOKEN_STRING:
                self.matchToken(StringT.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            case Number.TOKEN_STRING:
                self.matchToken(Number.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            case TrueValue.TOKEN_STRING:
                self.matchToken(TrueValue.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            case FalseValue.TOKEN_STRING:
                self.matchToken(FalseValue.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            case NullValue.TOKEN_STRING:
                self.matchToken(NullValue.TOKEN_STRING, self.tokenization[self.locationInTokenization])
                self.locationInTokenization += 1

            case _:
                try:
                    self.ParseObject()
                except: #If object fails then try array. If array fails then we should throw error anyways. 
                    self.ParseArray()

        if self.tokenization[self.locationInTokenization].type.TOKEN_STRING == Whitespace.TOKEN_STRING:
            self.matchToken(Whitespace.TOKEN_STRING, self.tokenization[self.locationInTokenization])
            self.locationInTokenization += 1

        print(f"Value has tokens from index {startTokenIndex} to index {self.locationInTokenization-1}")
    
        
def main():
    with open("testText.txt", newline='', mode="r") as file:
        stream: str = file.read()
        lexer: Lexer = Lexer(stream)
        lexer.scanStream()

    parser = Parser(lexer.streamTokenization)
    parser.ParseObject()

if __name__ == "__main__":
    main()