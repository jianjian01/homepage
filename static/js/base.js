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

function right_click_delete() {
    let site_names = document.getElementsByClassName('site-name');
    for (let s of site_names) {
        s.addEventListener('contextmenu', function (e) {
            // console.log(e);
            // e.preventDefault();
            // let menu = document.getElementsByClassName('context-menu')[0];
            // console.log(menu);
            // menu.style.display = 'block';
            // menu.style.left = e.x;
            // menu.style.top = e.y;
            // menu.classList.add('show');
            // return false;
        })
    }
}

function new_dom(tag, type, name, value, placeholder, class_list) {
    let dom = document.createElement(tag);
    dom.setAttribute('type', type);
    dom.setAttribute('name', name);
    dom.setAttribute('value', value);
    dom.setAttribute('placeholder', placeholder);
    for (let c of class_list) {
        dom.classList.add(c);
    }
    return dom;
}

function update_form(btn) {
    let csrf = document.head.querySelector("[name~=csrf-token][content]").content;
    // let form = btn.closest('.dropdown').getElementsByTagName('form')[0];
    let form = btn.closest('form');
    let csrf_dom = new_dom('input', 'hidden', 'csrf_token', csrf, '', []);
    let title_dom = new_dom('input', 'text', '', 'Add New Site', '',
        ["form-control-plaintext", "add-website-input", "form-control-sm"]);
    title_dom.readOnly = true;
    let name_dom = new_dom('input', 'text', 'name', '', 'site name',
        ["form-control", "add-website-input", "form-control-sm"]);
    name_dom.required = true;
    let url_dom = new_dom('input', 'url', 'url', '', 'https://example.com',
        ["form-control", "add-website-input", "form-control-sm"]);
    url_dom.required = true;

    let order_dom = new_dom('input', 'number', 'order', '', '1 - 1000',
        ["form-control", "add-website-input", "form-control-sm"]);
    order_dom.required = true;

    form.insertBefore(order_dom, form.firstChild);
    form.insertBefore(url_dom, order_dom);
    form.insertBefore(name_dom, url_dom);
    form.insertBefore(title_dom, name_dom);
    form.appendChild(csrf_dom);
}

function add_website_shortcut() {
    let close_btn = document.getElementsByClassName('close-dropdown-add-website');
    let submit_btn = document.getElementsByClassName('submit-dropdown-add-website');
    for (let btn of close_btn) {
        btn.onpointerdown = function (e) {
            $(e.target.closest('.dropdown-add-website')).dropdown('hide');
        };
        update_form(btn);
    }
}

add_website_shortcut();
right_click_delete();