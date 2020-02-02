function new_name_input_dom() {
    let name = document.createElement("input");
    name.setAttribute('type', 'text');
    name.setAttribute('class', 'new-cel-input');
    name.classList.add('name-cel');
    name.setAttribute('name', 'name');
    name.setAttribute('placeholder', '名称');
    name.required = true;
    name.autofocus = true;
    return name
}

function new_order_input_dom() {
    let order = document.createElement("input",);
    order.setAttribute('type', 'number');
    order.setAttribute('class', 'new-cel-input');
    order.classList.add('order-cel');
    order.setAttribute('placeholder', '10');
    order.setAttribute('min', '1');
    order.setAttribute('max', '1000');
    order.setAttribute('name', 'order');
    order.required = true;
    return order
}

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


// add new category
let btn_add = document.getElementById('btn-add-cate');
let cate = document.getElementById('main-category');
btn_add.onclick = function (e) {
    let tbody = cate.getElementsByTagName('tbody')[0];
    let row = tbody.insertRow();
    let num_cel = document.createElement("td");
    let name_cel = document.createElement("td");
    name_cel.setAttribute('class', 'new-cel');
    let name = new_name_input_dom();
    name_cel.appendChild(name);
    let order_cel = document.createElement("td");
    order_cel.setAttribute('class', 'new-cel');
    let order = new_order_input_dom();
    order_cel.appendChild(order);
    let action_cel = document.createElement("td");
    let action = document.createElement("span");
    action.innerText = "保存";
    action.setAttribute('class', 'save-new-cate');
    action.onpointerdown = save_new_cate;
    action_cel.appendChild(action);

    row.appendChild(num_cel);
    row.appendChild(name_cel);
    row.appendChild(order_cel);
    row.appendChild(action_cel);
};

// save new category
function save_new_cate(e) {
    let tr = e.target.closest('tr');
    let inputs = tr.getElementsByTagName('input');
    let name_val = "";
    let order_val = '';
    let ok = true;
    for (let i = 0; i < inputs.length; i++) {
        let dom = inputs.item(i);
        let name = dom.getAttribute('name');
        if (dom.checkValidity()) {
            dom.style.border = 'none';
        } else {
            dom.style.border = '1px solid red';
            dom.style.borderRadius = '5px';
            ok = false;
        }
        if (name === 'name') {
            name_val = dom.value;
        } else if (name === 'order') {
            order_val = dom.value;
        }
    }
    if (!ok) {
        return
    }

    let data = new FormData();
    data.set('name', name_val);
    data.set('order', order_val);


    http_request_json('POST', document.URL, data, refresh);
}

// delete category
function delete_cate(e) {
    let tr = e.target.closest('tr');
    let cate_id = tr.getAttribute('data-id');
    let data = new FormData();
    data.set('id', cate_id);
    http_request_json('DELETE', document.URL, data, refresh);
}

let delete_btn = document.getElementsByClassName('delete-cate');
for (let i = 0; i < delete_btn.length; i++) {
    let btn = delete_btn.item(i);
    btn.onpointerdown = delete_cate;
}


// update category
// change td content
function update_cate(e) {
    let tr = e.target.closest('tr');
    let tds = tr.getElementsByTagName('td');
    console.log(tds);
    let name_td = tds.item(0);
    let name_val = name_td.innerText;
    name_td.innerText = null;
    name_td.setAttribute('class', 'new-cel');
    let name = new_name_input_dom();
    name.setAttribute('value', name_val);
    name_td.appendChild(name);

    let order_td = tds.item(1);
    let order_val = order_td.innerText;
    let order = new_order_input_dom();
    order.setAttribute('value', order_val);
    order_td.innerText = '';
    order_td.appendChild(order);

    let action_td = tds.item(2);
    action_td.innerText = null;
    let action = document.createElement("span");
    action.innerText = "更新";
    action.setAttribute('class', 'save-update-cate');
    action.onpointerdown = save_update_cate;
    action_td.appendChild(action);
}

// send new content
function save_update_cate(e) {
    let tr = e.target.closest('tr');
    let cate_id = tr.getAttribute('data-id');
    let name_dom = tr.getElementsByClassName('name-cel');
    let order_dom = tr.getElementsByClassName('order-cel');
    let data = new FormData();
    data.set('id', cate_id);
    data.set('name', name_dom[0].value);
    data.set('order', order_dom[0].value);
    http_request_json('PUT', document.URL, data, refresh);

}

let update_btn = document.getElementsByClassName('update-cate');
for (let i = 0; i < update_btn.length; i++) {
    let btn = update_btn.item(i);
    btn.onpointerdown = update_cate;
}

