from typing import List, Type

from LexerTokens import Token 

class LexerToken:
    def __init__(self, value: str, type: Type[Token]) -> None:
        self.value: str = value
        self.type: Type[Token] = type

class Lexer:
    def __init__(self, inputStream: str) -> None:
        self.stream: str = inputStream
        self.locationInStream: int = 0
        self.streamLength: int = len(inputStream)
        self.streamTokenization: List[LexerToken] = []

    def scanStream(self) -> None:
        while(self.locationInStream < self.streamLength):
            tempStart: int = self.locationInStream
            for tokenClass in Token.registry:
                result: int = self.scanForToken(tokenClass)
                if result == -1: continue

                self.locationInStream = result + 1 #start should be the next char after this token
                if tempStart != self.locationInStream: self.streamTokenization.append(LexerToken(self.stream[tempStart:self.locationInStream], tokenClass))
                break

            if self.locationInStream == tempStart:
                print(f"Couldn't make token for {self.stream[tempStart]}")
                raise Exception("Failed to scan file")
            

    #Returns the final location of the token or -1 if failed   
    def scanForToken(self, token: Type[Token]) -> int:
        currentLocation: int = self.locationInStream
        state: int = 0
        while(currentLocation < self.streamLength):
            nextState: int = token.getNextState(state, self.stream[currentLocation])
            
            #If we reach this point that means next character is part of next token
            if nextState == -1: return currentLocation - 1 
            if nextState == -2: return -1

            currentLocation += 1
            state = nextState
        if state in token.getFinalStates(): return currentLocation - 1 #Current location is equal to len(stream) so return the length - 1
        return -1