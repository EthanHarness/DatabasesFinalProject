#Based on https://www.json.org/json-en.html
#All token classes return -1 if valid and -2 if invalid for their get next state function

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Type

DIGIT_ZERO_THROUGH_NINE: List[str] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
DIGIT_ONE_THROUGH_NINE: List[str] = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
HEXIDECIMAL_DIGITS: List[str] = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f',
    'A', 'B', 'C', 'D', 'E', 'F'
]
SCIENTIFIC_NOTATION_CHARACTERS: List[str] = ['e', "E"]
SIGN_CHARACTERS: List[str] = ['-', '+']

class Token(ABC):
    registry: List[Type[Token]] = []
    TOKEN_STRING: str

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not hasattr(cls, 'TOKEN_STRING') or cls.TOKEN_STRING == getattr(Token, 'TOKEN_STRING', None):
            raise TypeError(f"Class {cls.__name__} must define a 'TOKEN_STRING' class attribute.")
        Token.registry.append(cls)

    #Returns next state if able
    #Returns -1 if valid or -2 if invalid
    #Throws error if current state is not valid
    @staticmethod
    @abstractmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        pass

    #Returns all valid final states for a specific token
    @staticmethod
    @abstractmethod
    def getFinalStates() -> List[int]:
        pass


class Whitespace(Token):
    TOKEN_STRING: str = "Whitespace"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0:
                if nextCharacter == " ": return 1
                if nextCharacter == "\n": return 2 #Actual newlines treated as 1 character. 
                if nextCharacter == "\r": return 3
                if nextCharacter == "\t": return 4
                return -2
            case 1 | 2 | 3 | 4: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1,2,3,4]

class Number(Token):
    TOKEN_STRING: str = "Number"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0:
                if nextCharacter == "-": return 1
                if nextCharacter == "0": return 2
                if nextCharacter in DIGIT_ONE_THROUGH_NINE: return 3
                return -2 
            case 1: 
                if nextCharacter == "0": return 2
                if nextCharacter in DIGIT_ONE_THROUGH_NINE: return 3
                return -2
            case 2: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 4
                if nextCharacter == ".": return 5
                if nextCharacter in SCIENTIFIC_NOTATION_CHARACTERS: return 7
                return -1
            case 3: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 4
                if nextCharacter == ".": return 5
                if nextCharacter in SCIENTIFIC_NOTATION_CHARACTERS: return 7
                return -1
            case 4: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 4
                if nextCharacter == ".": return 5
                if nextCharacter in SCIENTIFIC_NOTATION_CHARACTERS: return 7
                return -1
            case 5: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 6
                return -2
            case 6: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 6
                if nextCharacter in SCIENTIFIC_NOTATION_CHARACTERS: return 7
                return -1
            case 7: 
                if nextCharacter in SIGN_CHARACTERS: return 8
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 9
                return -2
            case 8:
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 9
                return -2
            case 9: 
                if nextCharacter in DIGIT_ZERO_THROUGH_NINE: return 9
                return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [2,3,4,6,9]

class StringT(Token):
    TOKEN_STRING: str = "StringT"
    
    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0:
                if nextCharacter == "\"": return 1
                return -2
            case 1: 
                if nextCharacter == "\"": return 17
                if nextCharacter == "\\": return 2
                return 16
            case 2:
                if nextCharacter == "u": return 4
                if nextCharacter == "\"": return 8
                if nextCharacter == "\\": return 9
                if nextCharacter == "/": return 10
                if nextCharacter == "b": return 11
                if nextCharacter == "f": return 12
                if nextCharacter == "n": return 13
                if nextCharacter == "r": return 14
                if nextCharacter == "t": return 15
                return -2
            case 3: 
                if nextCharacter in HEXIDECIMAL_DIGITS: return 4
                return -2
            case 4: 
                if nextCharacter in HEXIDECIMAL_DIGITS: return 5
                return -2
            case 5: 
                if nextCharacter in HEXIDECIMAL_DIGITS: return 6
                return -2
            case 6: 
                if nextCharacter in HEXIDECIMAL_DIGITS: return 7
                return -2
            case 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
                if nextCharacter == "\\": return 2
                return 16
            case 16: 
                if nextCharacter == "\\": return 2
                if nextCharacter == "\"": return 17
                return 16
            case 17:  return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [17]

class TrueValue(Token):
    TOKEN_STRING: str = "TrueValue"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == 't': return 1
                return -2
            case 1: 
                if nextCharacter == 'r': return 2
                return -2
            case 2: 
                if nextCharacter == 'u': return 3
                return -2
            case 3: 
                if nextCharacter == 'e': return 4
                return -2
            case 4: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [4]
    
class FalseValue(Token):
    TOKEN_STRING: str = "FalseValue"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == 'f': return 1
                return -2
            case 1: 
                if nextCharacter == 'a': return 2
                return -2
            case 2: 
                if nextCharacter == 'l': return 3
                return -2
            case 3: 
                if nextCharacter == 's': return 4
                return -2
            case 4: 
                if nextCharacter == 'e': return 5
                return -2
            case 5: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [5]
    
class NullValue(Token):
    TOKEN_STRING: str = "NullValue"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == 'n': return 1
                return -2
            case 1: 
                if nextCharacter == 'u': return 2
                return -2
            case 2: 
                if nextCharacter == 'l': return 3
                return -2
            case 3: 
                if nextCharacter == 'l': return 4
                return -2
            case 4: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [4]
    
class LBracket(Token):
    TOKEN_STRING = "LeftBracket"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == '[': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]
    
class RBracket(Token):
    TOKEN_STRING = "RightBracket"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == ']': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]
    
class Comma(Token):
    TOKEN_STRING = "Comma"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == ',': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]
    
class Colon(Token):
    TOKEN_STRING = "Colon"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == ':': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]
    
class LBrace(Token):
    TOKEN_STRING = "LeftBrace"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == '{': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]
    
class RBrace(Token):
    TOKEN_STRING = "RightBrace"

    @staticmethod
    def getNextState(currentState: int, nextCharacter: str) -> int:
        match currentState:
            case 0: 
                if nextCharacter == '}': return 1
                return -2
            case 1: return -1
            case _: raise Exception("Invalid current state")

    @staticmethod
    def getFinalStates() -> List[int]:
        return [1]