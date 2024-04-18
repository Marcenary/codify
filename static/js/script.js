import { Compile } from '/static/js/compile.js'

const code = $('#code'), run = $('#run'), sel = $('select')
const compile = new Compile()

function sendSuccess() {
    const data = {
        status_task: 'success',
        id_task: document.location.href.split('/').slice(-1)[0],
        performed_task: JSON.parse(sessionStorage.getItem('task')).recipient
    }
    console.log(data)
    fetch("http://127.0.0.1:5000/task", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(data => {
        if (data.redirected)
            window.location.replace(data.url)
        else data = data.json()
        console.log(data)
    })
    .catch(err => console.log(err))
}

window.onload = e => {
	console.log("Load data!")
    fetch(`http://127.0.0.1:5000/get/task?id=${ document.location.href.split('/').slice(-1) }`, {
        method: 'GET', mode: 'cors',
        cache: 'no-cache', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow', referrerPolicy: 'no-referrer',
    })
    .then(data => data.json())
    .then(json => sessionStorage.setItem("task", JSON.stringify(json)))
    // если задание уже было пройдено не засчитывать ни опыт не кол-во вып.
    // записать в переменную и сравнивать
    // просто перенаправлять на главную без записи в бд
    if (localStorage.getItem("lang") != null)
        code.val(localStorage.getItem("code"))
}

setInterval(e => {
	if ( code.val() != localStorage.getItem("code") ) {
		console.log("Data save!")
		localStorage.setItem("code", code.val())
		localStorage.setItem("lang", sel.val())
	}
}, 15000)

function pyClick() {
    const data = {}
    data["code"] = code.val()
    data["run"]  = run.val()
    fetch("http://127.0.0.1:5000/compile", {
        method: 'POST', mode: 'cors',
        cache: 'no-cache', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        redirect: 'follow', referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    })
    .then(data => data.json())
    .then(json => {
        $('#log').text("")
        $('#log').text(json)

        json = json.map(i => (i != "True" && i != "False") ? i : (i == "True" ? true : false))
        json = json.every(i => i)
        if (json) {
            alert("Task fullfilled")
            document.querySelector('#submit').onclick = sendSuccess
        }

    }).catch(err => { console.log(err); alert("Ошибка в коде") })
}

function jsClick() {
    const data = {}
    data["code"] = code.val()
    data["run"]  = run.val()

    let res = compile.compile(data)

    $('#log').text("")
    $('#log').text(res)

    res = res.every(i => i)
    if (res) {
        alert("Task fullfilled")
        document.querySelector('#submit').onclick = sendSuccess
    }
}

sel.change(e => {
    const
        task  = JSON.parse(sessionStorage.getItem("task")),
        value = e.target.value == 'javascript' ? 'js' : e.target.value
    let all_code = compile.task(task.practic, task.otvet, value)
    code.val(all_code[0])
    run.val(all_code[1])
	
    if (value == 'js')
        $('#test').click(jsClick)
        // document.querySelector('#test').onclick = jsClick
	else if (value == 'python')
        $('#test').click(pyClick)
        // document.querySelector('#test').onclick = pyClick
    else if (value == 'none')
        $('#test').click(() => console.log("Choice lang"))
        // document.querySelector('#test').onclick = () => console.log("Choice lang")
})