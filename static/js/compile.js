export class Compile {
    constructor () {
        this.res = []
        this.template = {
            "main": {
                "python": `def func(arg):\n\treturn arg`,
                "javascript": `function func(arg) {\n\treturn arg;\n}`,
                "typescript": `function func(arg): any {\n\treturn arg;\n}`,
                "ruby": `def func(arg)\n\treturn arg\nend`,
                "php": `<?php\nfunction func($arg) {\n\treturn $arg;\n}`
            },
            "test": {
                "python": args => `from test import test\ndef main():\n\ttry:${ args }\n\texcept Exception as e: test(err=repr(error))\n\nif __name__ == '__main__':\n\tmain()`,
                "javascript": args => `const { test } = require("./test.js") function main() {\n\ttry {\n\treturn [${ args }\n\t]\n\t} catch (error) { test("", "", error.message) }\n}\n return main()`,
                "typescript": args => `import { test } from "./test.js"\nfunction main(): void {\n\ttry {${ args }\n\t} catch (error: any) { test("", "", error.message) }\n}\n\nmain()`,
                "ruby": args => `require_relative 'test'\ninclude Test\n\ndef main()${ args }\nrescue => error\n\tTest.test(err=error)\nend\n\nmain()`,
                "php": args => `<?php\ninclude("./test.php");\nfunction main() {\n\ttry {${ args }\n\t} catch (Exception $err) { test(null, null, $err); }\n}\nmain();`,
            }
        }

    }

    task(input, output, lang) {
        if (lang == "none") return ["", ""]
        let res = "pass", tmp = ""
        input  = JSON.parse(input)
        output = JSON.parse(output)

        for (let i = 0; i < input.length; ++i)
            tmp += `\n\t${ "ruby" == lang ? "Test." : "\t" }test(func('${ input[i] }'), '${ output[i] }')${ "php" == lang ? ';' : ("javascript" == lang ? ',' : '') }`
        
        res = this.template.test[lang](tmp)
        
        return [this.template["main"][lang], res]
    }

    compile(obj) {
        let jn = "\ttry {\
        \n\t\tfunction test(a=null, b=null, err=null) {\
        \n\t\t\tif (err != null) return err\
        \n\t\t\telse return a == b\
        \n\t\t}\n" + obj.code + "\n" + obj.run + "\
        \n\t} catch (e) { return e }", res
        if ( jn.indexOf('os') < 0 || jn.indexOf('eval') < 0 )
            res = new Function(jn)(this)
        console.log(res);
        return res
    }
}