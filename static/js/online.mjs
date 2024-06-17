function getCookie() {
    let arr = {}
    let tmp = document.cookie.split('; ')
    for (const key in tmp) {
        let i = tmp[key].split('=')
        arr[i[0]] = i[1]
    }
    return arr
}

// document.addEventListener("DOMContentLoaded", (event) => {
//     let cookie = getCookie()
//     if ("auth" in cookie && cookie.auth != "null")
//         fetch(document.location.origin + "/connect")
//     else console.log("Unauthorize");
// })

// window.addEventListener("beforeunload", (event) => {
//     // Отмените событие, как указано в стандарте.
//     event.preventDefault();
    
//     let cookie = getCookie()
//     if ("auth" in cookie && cookie.auth != "null")
//         fetch(document.location.origin + "/disconnect")
//     else console.log("Unauthorize");
    
//     // Chrome требует установки возвратного значения.
//     event.returnValue = "Вы точно хотите уйти?";
// })