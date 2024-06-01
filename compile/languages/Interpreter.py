import subprocess as subp
from .Interface import Interpreter

class Python(Interpreter):
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
        incl_p = "import os"
        func_p = "eval"
        if incl_p in code or func_p in code:
            return False, "PythonExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        try:
            with open("temp.py", "w") as f:
                f.write(self._code)
            
            os.system(self.opt.format("python", "temp.py"))
            with open("temp.txt", "r") as f:
                out = f.read()
        except Exception:
            return "error"

class JavaScript(Interpreter):
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
        incl_p = "require \"os\""
        func_p = "console.log"
        if incl_p in code or func_p in code:
            return False, "JavaScriptExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        try:
            with open("temp.js", "w") as f:
                f.write(self._code)
            
            os.system(self.opt.format("node", "temp.js"))
            with open("temp.txt", "r") as f:
                out = f.read()
        except Exception:
            return "error"

class TypeScript(Interpreter):
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
        incl_p = "import \"os\""
        func_p = "console.log"
        if incl_p in code or func_p in code:
            return False, "TypeScriptExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        try:
            with open("temp.ts", "w") as f:
                f.write(self._code)
            
            os.system(self.opt.format("tsc", "temp.ts")) # проверка на typescript ошибки
            os.system(self.opt.format("node", "temp.js"))

            with open("temp.txt", "r") as f:
                out = f.read()
        except Exception:
            return "error"

class Ruby(Interpreter):
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
        incl_p = "require \"os\""
        func_p = "puts"
        if incl_p in code or func_p in code:
            return False, "RubyExcepting: {error}"
        return True
    
    def _compile(self) -> list[bool]:
        try:
            with open("temp.rb", "w") as f:
                f.write(self._code)
            
            os.system(self.opt.format("ruby", "temp.rb"))
            with open("temp.txt", "r") as f:
                out = f.read()
        except Exception:
            return "error"