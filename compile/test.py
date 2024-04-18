def test(a: any=None, b: any=None, err: Exception=None) -> None:
    with open('out.txt', 'a+') as f:
        if err != None: f.write(err)
        else: f.write(str(a == b) + '\n')