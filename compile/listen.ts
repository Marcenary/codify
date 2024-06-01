import * as fs from 'fs'; // npm install -D @types/node

function test(a: any=null, b: any=null, err=null) {
    fs.appendFile("out.txt", err != null ? err : (a == b).toString(), err => (err != null ? console.log(err) : undefined))
}