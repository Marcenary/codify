import re
import subprocess as subp

from os import remove
from os.path import exists
import time
from .Interface import Compile

class Python(Compile):
    def __init__(self, name: str, code: str, user):
        super(Python, self).__init__(name, code, user)
        self.ext     = "py"
        self.program = "python3.10"
        self.testing_code = "def test(a: any=None, b: any=None, err: Exception=None) -> None:\n\twith open('{}', 'a+') as f:\n\t\tif err != None: f.write(err)\n\t\telse: f.write(str(a == b) + '\\n')"
    
    def __str__(self):
        return f"<Class'Python name={ self.name }>"

    def build(self) -> bool:
        valid = self._valid()
        
        if valid == True:
            read_file = self._compile()
            if read_file[0]:
                with open(read_file[1], 'r') as f:
                    self.result = f.read()            
                remove(read_file[1])
                return True

            else: self.result = read_file[1]
        else: self.result = valid[1]
        return False
    
    def _valid(self) -> bool|tuple:
        valid_search = {
            'import_exception': {
                # Можно обойти проверку на писав пробел + импорт(проверить!!!)
                'pattern': r'^import (os|sys|pip|tkinter)',
                'exception': "Такая библиотека не существует! (1)"
            },
            'import2_exception': {
                # Можно обойти проверку на писав пробел + импорт(проверить!!!)
                'pattern': r'^from (os|sys|pip|tkinter) import .*',
                'exception': "Такой библиотеки или функции не существует! (2)"
            },
            'function_exception': {
                'pattern': r'(eval|print|input|open)',
                'exception': "Такой функции не существует! (3)"
            },
        }
        for i in valid_search:
            res = re.search(valid_search[i]['pattern'], self._code, re.IGNORECASE|re.MULTILINE)
            if res != None:
                return False, f"PythonExcepting: { valid_search[i]['exception'] }"
        return True
    
    def _compile(self) -> tuple:
        '''Проверить дебагером созданные файлы, без debug=1!!!'''
        search = "{}{}.{}" # <task><name>.<ext> - функция тестирования, короткое имя задания, имя выполняющего задания, расширение файла
        try:
            name   = search.format(self.name, self.user, self.ext)
            result = search.format(self.name, self.user, "py.txt")
            
            if exists(name): remove(name)

            name   = f"compile/languages/python/{ name }"
            result = f"compile/languages/python/{ result }"
            with open(name, "w") as f:
                code = self.testing_code.format(result) + '\n\n' + self._code
                f.write(code.replace("from test import test", ''))

            process = subp.run([self.program, name], capture_output=True)
            error = process.stderr
            remove(name)

            if error != b'':
                raise Exception(error.decode())
            else: return True, result

        except Exception as e:
            return False, repr(e)

class JavaScript(Compile):
    def __init__(self, name: str, code: str, user):
        super(JavaScript, self).__init__(name, code, user)
        self.ext     = "js"
        self.program = "node"
        self.testing_code = "const fs = require(\"fs\")\nfunction test(a=null, b=null, err=null) {\n\tfs.appendFileSync('%s', (err != null ? err : `${ a == b }\\n`))\n}"
    
    def build(self) -> bool:
        valid = self._valid()
        
        if valid == True:
            read_file = self._compile()
            if read_file[0]:
                with open(read_file[1], 'r') as f:
                    self.result = f.read()            
                remove(read_file[1])
                return True

            else: self.result = read_file[1]
        else: self.result = valid[1]
        return False
    
    def _valid(self) -> bool|tuple:
        valid_search = {
            'require_exception': {
                # Можно обойти проверку написав пробел перед импортом(проверить!!!)
                # Можно обойти проверку передав аргумент, переменной(проверить!!!)
                'pattern': r'require\(.?(os|sys|fs|tkinter).?\)',
                'exception': "Такая библиотека не существует! (1)"
            },
            'import2_exception': {
                # Можно обойти проверку написав пробел + импорт(проверить!!!)
                'pattern': r'(\b|\s)import.+from .?(os|sys|time|tkinter).?',
                'exception': "Такой библиотеки или функции не существует! (2)"
            },
            'function_exception': {
                'pattern': r'(eval|console|input|open)',
                'exception': "Такой функции не существует! (3)"
            },
        }
        for i in valid_search:
            res = re.search(valid_search[i]['pattern'], self._code, re.IGNORECASE|re.MULTILINE)
            if res != None:
                return False, f"JavaScriptExcepting: { valid_search[i]['exception'] }"
        return True
    
    def _compile(self) -> list[bool]:
        search = "{}{}.{}" # <task><name>.<ext> - функция тестирования, короткое имя задания, имя выполняющего задания, расширение файла
        try:
            name   = search.format(self.name, self.user, self.ext)
            result = search.format(self.name, self.user, "js.txt")
            
            if exists(name): remove(name)

            name   = f"compile/languages/javascript/{ name }"
            result = f"compile/languages/javascript/{ result }"
            with open(name, "w") as f:
                code = self.testing_code%result + '\n\n' + self._code
                f.write(code.replace("const test = require(\"./test.js\")", ''))

            process = subp.run([self.program, name], capture_output=True)
            error = process.stderr
            remove(name)

            if error != b'':
                raise Exception(error.decode())
            else: return True, result

        except Exception as e:
            return False, repr(e)

class TypeScript(JavaScript):
    def __init__(self, name: str, code: str, user):
        super(TypeScript, self).__init__(name, code, user)
        self.ext     = "ts"
        self.program = "tsc"
        self.testing_code = "const fs = require(\"fs\")\nfunction test(a: any=null, b: any=null, err: any=null): void {\n\tfs.appendFileSync('%s', (err != null ? err : `${ a == b }\\n`))\n}"
    
    def _tsc(self) -> tuple:
        search = "{}{}.{}" # <task><name>.<ext> - функция тестирования, короткое имя задания, имя выполняющего задания, расширение файла
        try:
            name = search.format(self.name, self.user, self.ext)
            jname = search.format(self.name, self.user, "ts.js")
            if exists(name): remove(name)

            name = f"compile/languages/typescript/{ name }" # переместить над проверкой exists!
            jname = f"compile/languages/typescript/{ jname }" # переместить над проверкой exists!
            with open(name, "w") as f:
                code = self.testing_code%result + '\n\n' + self._code
                f.write(code.replace("import test from \"test.js\"", ''))

            process = subp.run([self.program, name], capture_output=True)
            error = process.stderr
            remove(name)

            with open(jname, "r") as f:
                self._code = f.read()

            if error != b'':
                raise Exception(error.decode())
            else: return True, None

        except Exception as e:
            return False, repr(e)

    def build(self) -> bool:
        valid = self._valid()
        success = self._tsc()

        if valid == True and success == True:
            read_file = self._compile()
            if read_file[0]:
                with open(read_file[1], 'r') as f:
                    self.result = f.read()            
                remove(read_file[1])
                return True
            
            else: self.result = read_file[1]
        else: self.result = valid[1] or success[1]
        return False
    
    def _valid(self) -> bool|tuple:
        valid_search = {
            'require_exception': {
                # Можно обойти проверку написав пробел перед импортом(проверить!!!)
                # Можно обойти проверку передав аргумент, переменной(проверить!!!)
                'pattern': r'require\(.?(os|sys|fs|tkinter).?\)',
                'exception': "Такая библиотека не существует! (1)"
            },
            'import2_exception': {
                # Можно обойти проверку написав пробел + импорт(проверить!!!)
                'pattern': r'(\b|\s)import.+from .?(os|sys|time|tkinter).?',
                'exception': "Такой библиотеки или функции не существует! (2)"
            },
            'function_exception': {
                'pattern': r'(eval|console|readline|open)',
                'exception': "Такой функции не существует! (3)"
            },
        }
        for i in valid_search:
            res = re.search(valid_search[i]['pattern'], self._code, re.IGNORECASE|re.MULTILINE)
            if res != None:
                return False, f"TypeScriptExcepting: { valid_search[i]['exception'] }"
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

class Ruby(Compile):
    def __init__(self, name: str, code: str, user):
        super(Ruby, self).__init__(name, code, user)
        self.ext     = "rb"
        self.program = "ruby"
        self.testing_code = "def test(a=nil, b=nil, err=nil)\n\tFile.open(\"%s\", \"a\") do |f|\n\t\tf.write(err != nil ? err : (a == b).to_s())\n\tend\nend"
    
    def build(self) -> bool:
        valid = self._valid()
        
        if valid == True:
            read_file = self._compile()
            if read_file[0]:
                with open(read_file[1], 'r') as f:
                    self.result = f.read()            
                remove(read_file[1])
                return True

            else: self.result = read_file[1]
        else: self.result = valid[1]
        return False
    
    def _valid(self) -> bool|tuple:
        valid_search = {
            'require_exception': {
                # Можно обойти проверку написав пробел перед импортом(проверить!!!)
                # Можно обойти проверку передав аргумент, переменной(проверить!!!)
                'pattern': r'require\(.?(os|sys|fs|tkinter).?\)',
                'exception': "Такая библиотека не существует! (1)"
            },
            'function_exception': {
                'pattern': r'(eval|puts|gets|File|exec)',
                'exception': "Такой функции не существует! (3)"
            },
        }
        for i in valid_search:
            res = re.search(valid_search[i]['pattern'], self._code, re.IGNORECASE|re.MULTILINE)
            if res != None:
                return False, f"RubyExcepting: { valid_search[i]['exception'] }"
        return True
    
    def _compile(self) -> list[bool]:
        search = "{}{}.{}" # <task><name>.<ext> - функция тестирования, короткое имя задания, имя выполняющего задания, расширение файла
        try:
            name   = search.format(self.name, self.user, self.ext)
            result = search.format(self.name, self.user, "rb.txt")
            
            if exists(name): remove(name)

            name   = f"compile/languages/ruby/{ name }"
            result = f"compile/languages/ruby/{ result }"
            with open(name, "w") as f:
                code = self.testing_code%result + '\n\n' + self._code
                code = code.replace("require_relative 'test'\ninclude Test", '')
                f.write(code.replace("Test.", ''))
            time.sleep(10)
            process = subp.run([self.program, name], capture_output=True)
            error = process.stderr
            remove(name)

            if error != b'':
                raise Exception(error.decode())
            else: return True, result

        except Exception as e:
            return False, repr(e)

class PHP(Compile):
    def __init__(self, name: str, code: str, user):
        super(PHP, self).__init__(name, code, user)
        self.ext     = "php"
        self.program = "php"
        self.testing_code = "function test($a=null, $b=null, $err=null) {\n\tfile_put_contents('%s', $err == null ? $a == $b : $err, FILE_APPEND);\n}"
    
    def __str__(self):
        return f"<Class'PHP name={ self.name }>"

    def build(self) -> bool:
        valid = self._valid()
        
        if valid == True:
            read_file = self._compile()
            if read_file[0]:
                with open(read_file[1], 'r') as f:
                    self.result = f.read()            
                remove(read_file[1])
                return True

            else: self.result = read_file[1]
        else: self.result = valid[1]
        return False
    
    def _valid(self) -> bool|tuple:
        valid_search = {
            # 'import_exception': {
            #     # Можно обойти проверку на писав пробел + импорт(проверить!!!)
            #     'pattern': r'^import (os|sys|pip|tkinter)',
            #     'exception': "Такая библиотека не существует! (1)"
            # },
            # 'import2_exception': {
            #     # Можно обойти проверку на писав пробел + импорт(проверить!!!)
            #     'pattern': r'^from (os|sys|pip|tkinter) import .*',
            #     'exception': "Такой библиотеки или функции не существует! (2)"
            # },
            'function_exception': {
                'pattern': r'(eval|exec|echo|print|print_r|var_dump|system)',
                'exception': "Такой функции не существует! (3)"
            },
        }
        for i in valid_search:
            res = re.search(valid_search[i]['pattern'], self._code, re.IGNORECASE|re.MULTILINE)
            if res != None:
                return False, f"PHPExcepting: { valid_search[i]['exception'] }"
        return True
    
    def _compile(self) -> tuple:
        search = "{}{}.{}"
        try:
            name   = search.format(self.name, self.user, self.ext)
            result = search.format(self.name, self.user, "php.txt")
            
            if exists(name): remove(name)

            name   = f"compile/languages/php/{ name }"
            result = f"compile/languages/php/{ result }"
            with open(name, "w") as f:
                code = self.testing_code.format(result) + '\n\n' + self._code
                f.write(code)

            process = subp.run([self.program, name], capture_output=True)
            error = process.stderr
            remove(name)

            if error != b'':
                raise Exception(error.decode())
            else: return True, result

        except Exception as e:
            return False, repr(e)