require("fs")

def test(a=nil, b=nil, err=nil)
    fs.appendFile("out.txt", err != nil ? err : (a == b).to_s(), err => (err != nil ? puts(err) : nil))
end