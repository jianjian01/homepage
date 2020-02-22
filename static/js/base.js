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


function append_website(data) {
    let container = document.getElementById('site-container');
    for (const site of data) {
        let dom = document.createElement('div');
        let header = document.createElement('div');
        header.classList.add("row");
        header.classList.add("site-header");
        header.classList.add("justify-content-between");

        let name = document.createElement('div');
        name.classList.add('col-8');
        let h5 = document.createElement('h5');
        h5.classList.add('sites');
        h5.classList.add('display-5');
        h5.classList.add('site-header-name');
        h5.innerText = site.name;
        name.appendChild(h5);

        header.appendChild(name);
        dom.appendChild(header);

        let hr = document.createElement('hr');
        hr.classList.add('site-hr');
        dom.appendChild(hr);

        let site_list = document.createElement('div');
        site_list.classList.add('row');
        site_list.classList.add('p-3');
        site_list.classList.add('site-list');

        for (const s of site.website) {
            let item = document.createElement('div');
            item.classList.add('col-4');
            item.classList.add('col-lg-2');
            item.classList.add('site-item');
            let a_dom = document.createElement('a');
            a_dom.setAttribute('href', s.url);
            a_dom.setAttribute('target', '_blank');
            let url = new URL('/site/${s.icon}.png', "https://website.chidian.xin");
            a_dom.setAttribute('style', "background-image: url(" + url.toString() + ")");
            a_dom.innerText = s.name;
            item.appendChild(a_dom);
            site_list.appendChild(item);
        }
        dom.appendChild(site_list);
        container.appendChild(dom);
    }
}


add_website_shortcut();
right_click_delete();