import subprocess as subp
from .Interface import Compilate

class CLang(Compilate):
    def __init__(self, name):
        super()
        self._code = ""
        self.name  = name
    
    def build(self, code1, code2) -> bool:
        code  = code1 + code2
        valid = self._valid(code)
        if valid == True:
            self._code = code
            return True
        
        raise Exception(valid[1])
    
    def _valid(self, code: str) -> bool|tuple:
        # import re
        incl_p = "#include <stdlib.h>"
        func_p = "printf"
        if incl_p in code or func_p in code:
            return False, "CLangExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        with open("main.c", "w") as f:
            f.write(self._code)
            os.system(self.opt.format("gcc", "-Fshared temp.c"))
        
        try:
            import ctypes
            main = ctypes.CDLL("temp.dll")
            out  = main.__dict__(self.name)
        except Exception:
            return "error"

class CPlusPlus(Compilate):
    def __init__(self, name):
        super()
        self._code = ""
        self.name  = name
    
    def build(self, code1, code2) -> bool:
        code  = code1 + code2
        valid = self._valid(code)
        if valid == True:
            self._code = code
            return True
        
        raise Exception(valid[1])
    
    def _valid(self, code: str) -> bool|tuple:
        # import re
        incl_p = "#include <iostream>"
        func_p = "cout"
        if incl_p in code or func_p in code:
            return False, "CPlusPlusExcepting: _"
        return True
    
    def _compile(self) -> list[bool]:
        with open("main.cpp", "w") as f:
            f.write(self._code)
            os.system(self.opt.format("g++", "-Fshared temp.cpp"))
        
        try:
            import ctypes
            main = ctypes.CDLL("temp.dll")
            out  = main.__dict__(self.name)
        except Exception:
            return "error"

class CSharp(Compilate):
    def __init__(self, name):
        super()
        self._code = ""
        self.name  = name
    
    def build(self, code1, code2) -> bool:
        code  = code1 + code2
        valid = self._valid(code)
        if valid == True:
            self._code = code
            return True
        
        raise Exception(valid[1])
    
    def _valid(self, code: str) -> bool|tuple:
        # import re
        incl_p = "using System;"
        func_p = "Console"
        if incl_p in code or func_p in code:
            return False, "CSharpExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        with open("main.cs", "w") as f:
            f.write(self._code)
            os.system(self.opt.format("cs", "? temp.cs"))
        
        try:
            import ctypes
            main = ctypes.WinDLL("temp.dll")
            out  = main.__dict__(self.name)
        except Exception:
            return "error"

class Java(Compilate):
    def __init__(self, name):
        super()
        self._code = ""
        self.name  = name
    
    def build(self, code1, code2) -> bool:
        code  = code1 + code2
        valid = self._valid(code)
        if valid == True:
            self._code = code
            return True
        
        raise Exception(valid[1])
    
    def _valid(self, code: str) -> bool|tuple:
        # import re
        incl_p = "? ?"
        func_p = "System"
        if incl_p in code or func_p in code:
            return False, "JavaExcepting: _"
        return True
    
    def _compile(self) -> list[bool]:
        with open("main.java", "w") as f:
            f.write(self._code)
            os.system(self.opt.format("javac", "temp/temp.java")) # name folder/name class.java
        
        try:
            subp.run("java", "-jar", "jython-standalone-2.7.3.jar", "temp.py")
            with open("temp.txt", "r") as f:
                out = f.read()
        except Exception:
            return "error"