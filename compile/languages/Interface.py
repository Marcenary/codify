from abc import ABC, abstractmethod

class Compile(ABC):
    result  = ""
    ext     = ""
    program = ""

    def __init__(self, name: str, code: str, user):
        self._code = code
        self.name  = name
        self.user  = user

    @abstractmethod
    def build(self, code1, code2) -> bool: pass
    
    @abstractmethod
    def _valid(self, code: str) -> bool|tuple: pass