const fs = require("fs")
function test(a=null, b=null, err=null) {
    fs.appendFile("out.txt", err != null ? err : (a == b).toString(), err => (err != null ? console.log(err) : undefined))
}