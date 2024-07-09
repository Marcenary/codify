import { Compile } from '/static/js/compile.js'

const
    editor   = ace.edit("editor"),
    readonly = ace.edit("run"),
    sel      = $('#select'),
    compile  = new Compile(),
    num = document.location.href.split('/').slice(-1)

function editorSetup(lang) {
    let theme = "ace/theme/one_dark";

    editor.setTheme(theme);
    editor.commands.addCommand({
        name: 'myTestingCommand',
        bindKey: { win: 'Ctrl-S',  mac: 'Command-S' },
        exec: editor => { $("#test").click() },
        readOnly: true,
    });
    
    readonly.setTheme(theme);
    readonly.setReadOnly(true);

    editor.setValue("")
    readonly.setValue("")
    
    $('#editor').css("fontSize", '16px');
    $('#run').css("fontSize", '16px');
}

function sendSuccess() {
    const data = {
        status_task: 'success',
        id_task: document.location.href.split('/').slice(-1)[0],
        performed_task: JSON.parse(sessionStorage.getItem('task')).recipient,
        code: editor.getValue(),
        lang: sel.text()
    }
    console.log(data)
    
    fetch(`${ document.location.origin }/tasks/task`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(data => {
        if (data.redirected) window.location.replace(data.url)
        else data = data.json()
        console.log(data)
    })
    .catch(err => console.log(err))
}

window.onload = e => {
    fetch(`${ document.location.origin }/api/v1/get/task?id=${ document.location.href.split('/').slice(-1) }`, {
        method: 'GET', mode: 'cors',
        cache: 'no-cache', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow', referrerPolicy: 'no-referrer',
    })
    .then(data => data.json())
    .then(json => sessionStorage.setItem("task", JSON.stringify(json)))
    // console.log("Load data!")
    editorSetup()

    // if (localStorage.getItem("lang") != null)
    //     editor.setValue(localStorage.getItem("code"))
}

setInterval(e => {
	if ( editor.getValue() != localStorage.getItem("code") ) {
		console.log(`Data save! - ${ sel.text() }`)
		localStorage.setItem("code", editor.getValue())
		localStorage.setItem("lang", sel.text())
	}
}, 10000)

// for all
function pyClick() {
    let link;
    const data = {
        lang: sel.text(),
        name: `Task${ num }`,
        code: `${ editor.getValue() }\n\n${ readonly.getValue() }`,
    }
    
    if (data.lang == "Python")
        link = `/tasks/compile`
    if (data.lang == "TypeScript")
        link = `/tasks/compile/type`
    if (data.lang == "Ruby")
        link = `/tasks/compile/ruby`
    if (data.lang == "PHP") {
        link = `/tasks/compile/php`
        let tmp = readonly.getValue().replace("<?php\n", "")
        data.code = `${ editor.getValue() }\n\n${ tmp }`
    }

    fetch(`${ document.location.origin }${link}`, {
        method: 'POST', mode: 'cors',
        cache: 'no-cache', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow', referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    })
    .then(data => data.json())
    .then(json => {
        console.log(json);
        $('#log').text("")

        if (json.status == "failed") {
            $('#log').html(json.result.replace(/\\(n|'|")/g, '\n')
            .split('\n')
            .map(i => i + '<br>'))
            return
        }
        json = json.result.map(i => i.toUpperCase())
        let res = json.join()
        
        json = json.map(i => ( "TRUE" != i && "FALSE" != i) ? i : ("TRUE" == i ? true : false))
        json = json.every(i => i)
        
        res = res.replace(/TRUE,?/g, "<span class='text-success'>Верное решение<span><br>")
        if (json) {
            $("#test").removeClass("btn-primary")
            $("#test").addClass("btn-outline-primary")
            $("#submit").removeClass("btn-outline-success")
            $("#submit").addClass("btn-success")
            document.querySelector('#submit').onclick = sendSuccess
        }
        else res = res.replace(/FALSE,?/g, "<span class='text-danger'>Не верное значение</span><br>")
        $('#log').html(res)

    }).catch(err => { console.log(err); })
}

function jsClick() {
    const data = {}
    data["code"] = editor.getValue()
    data["run"]  = readonly.getValue()
    
    let res = compile.compile(data)
    
    $('#log').text("")
    $('#log').text(res)
    
    console.log(res);
    res = res.every(i => i)
    if (res) {
        alert("Task fullfilled")
        document.querySelector('#submit').onclick = sendSuccess
    }
}

$(".lang").click(e => {
    $('#select').text(e.target.value);
    const
        task  = JSON.parse(sessionStorage.getItem("task")),
        value = {
            none: 'none',
            Python: 'python',
            JavaScript: 'javascript',
            TypeScript: 'typescript',
            Ruby: 'ruby',
            PHP: 'php'
        }[e.target.value],
        cache_lang = localStorage.getItem("lang")

    let all_code = compile.task(task.practic, task.otvet, value)

    console.log(cache_lang != null)
    if (cache_lang != null && cache_lang.toLowerCase() == value)
        editor.setValue(localStorage.getItem("code"))
    else
        editor.setValue(all_code[0])
    readonly.setValue(all_code[1])

    editor.session.setMode(`ace/mode/${value}`)
    readonly.session.setMode(`ace/mode/${value}`)    
    
    if (value == 'python')
        $('#test').click(pyClick)
    if (value == 'ruby')
        $('#test').click(pyClick)
    if (value == 'php')
        $('#test').click(pyClick)
    if (value == 'javascript')
        $('#test').click(jsClick)
    if (value == 'typescript')
        $('#test').click(pyClick)
    if (value == 'none')
        $('#test').click(() => console.log("Choice lang"))
})