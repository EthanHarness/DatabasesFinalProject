from typing import List, Type

from JsonParser.JsonLexer import Lexer, LexerToken
from JsonParser.LexerTokens import Token, Whitespace

class LexerShouldFailException(Exception):
    pass

def TestTokenizations():
    def createLexerAndScan(inputText: str) -> Lexer:
        lexer: Lexer = Lexer(inputText)
        lexer.scanStream()
        return lexer
    
    def assertAgainstLexerTokens(expectedTokens: List[LexerToken], actualTokens: List[str], errorMsg: str) \
            -> None:
        
        assert len(expectedTokens) == len(actualTokens), "Length mismatch failure"
        for lexTok,actualTokenString in zip(expectedTokens, actualTokens):
            assert lexTok.type.TOKEN_STRING == actualTokenString, errorMsg

    def testTokenization(inputText: str, expectedTokenStrings: List[str], errorMsg: str) -> None:
        lex = createLexerAndScan(inputText)
        assertAgainstLexerTokens(lex.streamTokenization, expectedTokenStrings, errorMsg)

    def testAndFailLexer(inputText: str, errorMsg: str) -> None:
        try:
            createLexerAndScan(inputText)
            raise LexerShouldFailException(errorMsg)
        except LexerShouldFailException:
            raise
        except Exception as e:
            pass


    def testWhiteSpaceTokenization() -> None:
        errorMsg = "Whitespace unit tests failed"
        testTokenization(" ", [Whitespace.TOKEN_STRING], errorMsg)
        testTokenization("\n", [Whitespace.TOKEN_STRING], errorMsg)
        testTokenization("\t", [Whitespace.TOKEN_STRING], errorMsg)
        testTokenization("\r", [Whitespace.TOKEN_STRING], errorMsg)
        testTokenization("\r \n \t \t\t\r", [Whitespace.TOKEN_STRING], errorMsg)

        print("Whitespace Unit Tests Passed")

    testWhiteSpaceTokenization()


def TestLexer(filePath: str = ""):
    with open(filePath, newline='', mode="r") as file:
        stream: str = file.read()
        lexer: Lexer = Lexer(stream)
        lexer.scanStream()
    print(lexer.streamTokenization)

def main():
    path = "./Tests/UnitTestsText.txt"
    TestTokenizations()



if __name__ == "__main__":
    main()