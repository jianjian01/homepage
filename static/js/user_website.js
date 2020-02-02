function add_new_website(e) {
    console.log(e);

    let tr_dom = document.createElement("tr");
    tr_dom.classList.add('site-site');

    // th
    let th_dom = document.createElement('th');
    th_dom.setAttribute('scope', 'row');
    tr_dom.appendChild(th_dom);

    // name
    let td_name_dom = document.createElement('td');
    td_name_dom.classList.add('site-name');
    td_name_dom.classList.add('new-site-name');
    td_name_dom.classList.add('new-site-td');
    let name_input_dom = document.createElement('input');
    name_input_dom.setAttribute('name', 'name');
    name_input_dom.setAttribute('type', 'text');
    name_input_dom.required = true;
    name_input_dom.autofocus = true;
    name_input_dom.classList.add('new-website-input-dom');
    name_input_dom.classList.add('new-site-name-input');
    name_input_dom.setAttribute('placeholder', 'name');
    td_name_dom.appendChild(name_input_dom);
    tr_dom.appendChild(td_name_dom);

    // url
    let td_url_dom = document.createElement('td');
    td_url_dom.classList.add('site-url');
    td_url_dom.classList.add('new-site-url');
    td_url_dom.classList.add('new-site-td');
    let url_input_dom = document.createElement("input");
    url_input_dom.classList.add('url-input-dom');
    url_input_dom.classList.add('new-website-input-dom');
    url_input_dom.setAttribute('name', 'url');
    url_input_dom.setAttribute('type', 'url');
    url_input_dom.setAttribute('placeholder', 'https://example.com');
    url_input_dom.required = true;
    td_url_dom.appendChild(url_input_dom);
    tr_dom.appendChild(td_url_dom);

    // order
    let td_order_dom = document.createElement('td');
    td_order_dom.classList.add('site-order');
    td_order_dom.classList.add('new-site-order');
    td_order_dom.classList.add('new-site-td');
    let order_input_dom = document.createElement("input");
    order_input_dom.setAttribute('name', 'order');
    order_input_dom.classList.add('order-input-dom');
    order_input_dom.setAttribute('type', 'number');
    order_input_dom.setAttribute('min', '1');
    order_input_dom.setAttribute('max', '1000');
    order_input_dom.setAttribute('placeholder', '10');
    order_input_dom.required = true;
    order_input_dom.classList.add('new-website-input-dom');
    td_order_dom.appendChild(order_input_dom);
    tr_dom.appendChild(td_order_dom);

    // action
    let td_action_dom = document.createElement('td');
    td_action_dom.classList.add('new-site-td');
    td_action_dom.classList.add('site-action');
    td_action_dom.classList.add('new-site-action');
    let span_action_dom = document.createElement('span');
    span_action_dom.innerText = '保存';
    span_action_dom.onpointerdown = save_new_website;
    td_action_dom.appendChild(span_action_dom);
    tr_dom.appendChild(td_action_dom);

    let site_list = e.target.parentNode.parentNode;
    let cate_id = site_list.getAttribute("data-id");
    tr_dom.setAttribute('date-cate-id', cate_id);
    let tbody = site_list.getElementsByTagName('tbody')[0];
    tbody.appendChild(tr_dom)
}

function save_new_website(e) {
    let tr_dom = e.target.closest('tr');
    let input_doms = tr_dom.getElementsByTagName('input');
    let name_input_dom = tr_dom.getElementsByClassName('new-site-name-input')[0];
    let url_input_dom = tr_dom.getElementsByClassName('url-input-dom')[0];
    let order_input_dom = tr_dom.getElementsByClassName('order-input-dom')[0];

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
    if (!ok) {
        return
    }

    let cate_id_val = tr_dom.getAttribute('date-cate-id');
    let name_val = name_input_dom.value;
    let url_val = url_input_dom.value;
    let order_val = order_input_dom.value;

    if (order_val.length === 0) {
        order_val = '10'
    }
    let data = new FormData();
    data.append('name', name_val);
    data.append('cate_id', cate_id_val);
    data.append('url', url_val);
    data.append('order', order_val);

    http_request_json('POST', document.URL, data, refresh)
}

function delete_website(e) {
    let tr = e.target.closest('tr');
    let website_id = tr.getAttribute('data-id');
    let data = new FormData();
    data.append('id', website_id);
    http_request_json('DELETE', document.URL, data, refresh)
}

function run() {
    let add_btn = document.getElementsByClassName('add-new-website');
    let delete_btn = document.getElementsByClassName('delete-site');
    for (let btn of add_btn) {
        btn.onpointerdown = add_new_website;
    }
    for (let btn of delete_btn) {
        btn.onpointerdown = delete_website;
    }

}

window.onload = run;
