from abc import ABC, abstractmethod

class Compile(ABC):
    opt = "{} {}" # for all lang calls

    @abstractmethod
    def build(self, code1, code2) -> bool: pass
    
    @abstractmethod
    def _valid(self, code: str) -> bool|tuple: pass

class Interpreter(Compile):
    def _interprete(self) -> list[bool]: pass

class Compilate(Compile):
    def _compile(self) -> list[bool]: pass