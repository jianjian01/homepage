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

function show_login_modal() {
    // 弹出登录层
    let btn = document.getElementById('header-login-button');
    let modal = document.getElementById("login-modal");
    let close = document.getElementsByClassName("close")[0];
    if (btn === null) {
        return
    }
    btn.onclick = function (e) {
        modal.style.display = "block";
    };
    close.onclick = function (e) {
        modal.style.display = "none";
    };

}

function dropdown_action() {
    let dropdown = document.getElementsByClassName('dropdown');
    for (let i = 0; i < dropdown.length; i++) {
        let dp = dropdown.item(i);
        dp.onclick = function (e) {
            console.log(e);
            let target = dp.getElementsByClassName('dropdown-content')[0];
            let display = 'none';
            if (target.style.display === 'none') {
                display = 'block'
            }
            target.style.display = display;
        };
        // dp.onpointerleave = function (e) {
        //     let target = dp.getElementsByClassName('dropdown-content')[0];
        //     target.style.display = 'none'
        // };
    }
}

window.onclick = function (event) {
    let dropdown = document.getElementsByClassName('dropdown');

    for (let i = 0; i < dropdown.length; i++) {
        let dp = dropdown.item(i);
        let content = dp.getElementsByClassName('dropdown-content')[0];
        if (event.target !== dp) {
            let inner = false;
            for (let ele of dp.children) {
                if (ele === event.target) {
                    inner = true
                }
            }
            if (!inner) {
                content.style.display = 'none'
            }
        }
    }

    let modal = document.getElementById("login-modal");
    if (modal !== null && event.target === modal) {
        modal.style.display = "none";
    }
};

function run() {
    show_login_modal();
    dropdown_action();
}

run();
