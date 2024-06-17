import { Compile } from '/static/js/compile.js'

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

const
    editor   = ace.edit("editor"),
    readonly = ace.edit("run"),
    sel      = $('#select'),
    compile  = new Compile()

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
    console.log("Load data!")
    editorSetup()
    // если задание уже было пройдено не засчитывать ни опыт не кол-во вып.
    // записать в переменную и сравнивать
    // просто перенаправлять на главную без записи в бд
    if (localStorage.getItem("lang") != null)
        editor.setValue(localStorage.getItem("code"))
}

setInterval(e => {
	if ( editor.getValue() != localStorage.getItem("code") ) {
		console.log("Data save!")
		localStorage.setItem("code", editor.getValue())
		localStorage.setItem("lang", sel.text())
	}
}, 15000)

// for all
function pyClick() {
    const data = {
        lang: sel.text(),
        name: 0,
        code: `${ editor.getValue() }\n\n${ readonly.getValue() }`,
    }
    
    // if (data.lang == "Python")
    // if (data.lang == "JavaScript")
    // if (data.lang == "TypeScript")
    // if (data.lang == "Ruby")
    // if (data.lang == "PHP")
    
    fetch(`${ document.location.origin }/tasks/compile`, {
        method: 'POST', mode: 'cors',
        cache: 'no-cache', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow', referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    })
    .then(data => data.json())
    .then(json => {
        $('#log').text("")
        json[0].split(/\b/)
        let res = json.join(''), out = ''
        console.log(res);
        
        json = json.map(i => (i != "True" && i != "False") ? i : (i == "True" ? true : false))
        json = json.every(i => i)

        res = res.replace(/True/g, "<span class='text-success'>Верное решение<span><br>")
        if (json) {
            $("#test").removeClass("btn-primary")
            $("#test").addClass("btn-outline-primary")
            $("#submit").removeClass("btn-outline-success")
            $("#submit").addClass("btn-success")
            document.querySelector('#submit').onclick = sendSuccess
        }
        else res = res.replace(/False/g, "<span class='text-danger'>Не верное значение</span><br>")
        $('#log').html(res)

    }).catch(err => { console.log(err); })
}

function jsClick() {
    const data = {}
    data["code"] = editor.getValue()
    data["run"]  = readonly.getValue()

    console.log(data);

    let res = compile.compile(data)

    $('#log').text("")
    $('#log').text(res)

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
        }[e.target.value]

    let all_code = compile.task(task.practic, task.otvet, value)
    editor.setValue(all_code[0])
    readonly.setValue(all_code[1])

    editor.session.setMode(`ace/mode/${value}`)
    readonly.session.setMode(`ace/mode/${value}`)
	
    if (value == 'javascript')
        $('#test').click(jsClick)
	else if (value == 'python')
        $('#test').click(pyClick)
    else if (value == 'none')
        $('#test').click(() => console.log("Choice lang"))
})