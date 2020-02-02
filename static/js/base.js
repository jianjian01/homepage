function http_request_json(action, url, data, callback) {
    let request = new XMLHttpRequest();
    request.open(action, url, true);
    request.addEventListener("load", callback);
    data.set('csrf_token', document.head.querySelector("[name~=csrf-token][content]").content);
    request.send(data);
}

function refresh(event) {
    window.location = window.location.href;
}

function run() {
    let dropdown = document.getElementsByClassName('dropdown');
    for (let i = 0; i < dropdown.length; i++) {
        let dp = dropdown.item(i);
        dp.onpointerenter = function (e) {
            let target = dp.getElementsByClassName('dropdown-content')[0];
            target.style.display = 'block'
        };
        dp.onpointerleave = function (e) {
            let target = dp.getElementsByClassName('dropdown-content')[0];
            target.style.display = 'none'
        };
    }
}

window.onload = run;
