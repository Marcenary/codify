export class Compile {
    constructor () {
        this.res = []
        this.template = {
            "main": {
                "python": "def func():\n\treturn",
                "js": "function func() {\n\t\n}",
                "none": ""
            },
            "test": {
                "python": [
                    "from test import test\ndef main():\n\ttry:",
                    "",
                    "\texcept Exception as e: test(err=repr(e))\n\nif __name__ == '__main__':\n\tmain()"
                ],
                "js": [
                    "function main() {\n\treturn [",
                    "",
                    "\t]\n}\nreturn main()"
                ],
                "none": ["", "", ""]
            }
        }

    }

    task(input, output, lang) {
        if (lang == "none") return ["", ""]
        let temp = ""
        input    = JSON.parse(input)
        output   = JSON.parse(output)
        temp    += this.template["test"][lang][0]

        for (let i = 0; i < input.length; ++i)
            temp += this.template["test"][lang][1] + `\n\t\ttest(func('${ input[i] }'), '${ output[i] }')${ lang == "js" ? ',' : '' }`
        temp += "\n"
        temp += this.template["test"][lang][2]
        
        return [this.template["main"][lang], temp]
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
        return res
    }
}