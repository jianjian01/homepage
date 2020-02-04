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

function new_input_dom(name, type, placeholder, required, autofocus) {
    let name_dom = document.createElement("input");
    name_dom.setAttribute('type', type);
    name_dom.classList.add('new-cel-input');
    name_dom.setAttribute('name', name);
    name_dom.setAttribute('placeholder', placeholder);
    name_dom.required = required;
    name_dom.autofocus = autofocus;
    return name_dom
}

function new_save_btn() {
    let action = document.createElement("span");
    action.innerText = "保存";
    action.classList.add('save-new-btn');
    return action
}

function input_valid(input_doms) {
    let ok = true;
    for (let dom of input_doms) {
        if (dom.checkValidity()) {
            dom.style.border = 'none';
        } else {
            dom.style.border = '1px solid red';
            dom.style.borderRadius = '5px';
            ok = false;
        }
    }
    return ok
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
