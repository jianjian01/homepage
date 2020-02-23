function new_order_input_dom() {
    let order = document.createElement("input",);
    order.setAttribute('type', 'number');
    order.setAttribute('class', 'new-cel-input');
    order.setAttribute('placeholder', '1 - 1000');
    order.setAttribute('min', '1');
    order.setAttribute('max', '1000');
    order.setAttribute('name', 'order');
    order.required = true;
    return order
}

// add new category
function add_new_category(e) {
    let cate = document.getElementById('main-category');
    let tbody = cate.getElementsByTagName('tbody')[0];
    let row = tbody.insertRow();
    let num_cel = document.createElement("td");
    let name_cel = document.createElement("td");
    name_cel.setAttribute('class', 'new-cel');
    let name = new_input_dom('name', 'text', 'name', true, true);
    name.classList.add('new-cel-input');
    name.classList.add('name-cel-input');
    name_cel.appendChild(name);
    let order_cel = document.createElement("td");
    order_cel.setAttribute('class', 'new-cel');
    let order = new_order_input_dom();
    order.classList.add('order-cel-input');
    order_cel.appendChild(order);
    let action_cel = document.createElement("td");
    let action = document.createElement("span");
    action.innerText = "保存";
    action.classList.add('save-new-btn');
    action.classList.add('save-new-cate');
    action.onpointerdown = save_new_cate;
    action_cel.appendChild(action);

    row.appendChild(num_cel);
    row.appendChild(name_cel);
    row.appendChild(order_cel);
    row.appendChild(action_cel);
}

// save new category
function save_new_cate(e) {
    let tr = e.target.closest('tr');
    let inputs = tr.getElementsByTagName('input');
    let name_val = "";
    let order_val = '';
    for (let i = 0; i < inputs.length; i++) {
        let dom = inputs.item(i);
        let name = dom.getAttribute('name');
        if (name === 'name') {
            name_val = dom.value;
        } else if (name === 'order') {
            order_val = dom.value;
        }
    }
    if (!input_valid(inputs)) {
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
    let name = new_input_dom('name', 'text', 'name', true, true);
    name.classList.add('name-cel-input');
    name.setAttribute('value', name_val);
    name_td.appendChild(name);

    let order_td = tds.item(1);
    let order_val = order_td.innerText;
    let order = new_order_input_dom();
    order.classList.add('order-cel-input');
    order.setAttribute('value', order_val);
    order_td.innerText = '';
    order_td.appendChild(order);

    let action_td = tds.item(2);
    action_td.innerText = null;
    let action = document.createElement("span");
    action.innerText = "更新";
    action.setAttribute('class', 'update-btn');
    action.onpointerdown = save_update_cate;
    action_td.appendChild(action);
}

// send new content
function save_update_cate(e) {
    let tr = e.target.closest('tr');
    let cate_id = tr.getAttribute('data-id');
    let name_dom = tr.getElementsByClassName('name-cel-input');
    let order_dom = tr.getElementsByClassName('order-cel-input');
    let data = new FormData();
    data.set('id', cate_id);
    data.set('name', name_dom[0].value);
    data.set('order', order_dom[0].value);
    http_request_json('PUT', document.URL, data, refresh);

}

function category_action() {
    let update_btn = document.getElementsByClassName('update-cate');
    let delete_btn = document.getElementsByClassName('delete-cate');
    let btn_add = document.getElementById('btn-add-cate');

    for (let btn of update_btn) {
        btn.onpointerdown = update_cate;
    }

    for (let btn of delete_btn) {
        btn.onpointerdown = delete_cate;
    }
    btn_add.onpointerdown = add_new_category;
}

category_action();

