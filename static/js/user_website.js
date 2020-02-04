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
    td_name_dom.classList.add('new-cel');
    let name_input_dom = new_input_dom('name', 'text', 'name', true, true);
    name_input_dom.classList.add('name-cel');
    name_input_dom.classList.add('new-cel-input');
    td_name_dom.appendChild(name_input_dom);
    tr_dom.appendChild(td_name_dom);

    // url
    let td_url_dom = document.createElement('td');
    td_url_dom.classList.add('new-cel');
    let url_input_dom = document.createElement("input");
    url_input_dom.classList.add('url-cel');
    url_input_dom.classList.add('new-cel-input');
    url_input_dom.setAttribute('name', 'url');
    url_input_dom.setAttribute('type', 'url');
    url_input_dom.setAttribute('placeholder', 'https://example.com');
    url_input_dom.required = true;
    td_url_dom.appendChild(url_input_dom);
    tr_dom.appendChild(td_url_dom);

    // order
    let td_order_dom = document.createElement('td');
    td_order_dom.classList.add('new-cel');
    let order_input_dom = document.createElement("input");
    order_input_dom.setAttribute('name', 'order');
    order_input_dom.classList.add('new-cel-input');
    order_input_dom.classList.add('order-cel');
    order_input_dom.setAttribute('type', 'number');
    order_input_dom.setAttribute('min', '1');
    order_input_dom.setAttribute('max', '1000');
    order_input_dom.setAttribute('placeholder', '10');
    order_input_dom.required = true;
    td_order_dom.appendChild(order_input_dom);
    tr_dom.appendChild(td_order_dom);

    // action
    let td_action_dom = document.createElement('td');
    td_action_dom.classList.add('new-cel');
    td_action_dom.classList.add('site-action');
    let save = new_save_btn();
    save.onpointerdown = save_new_website;
    td_action_dom.appendChild(save);
    tr_dom.appendChild(td_action_dom);

    let site_list = e.target.parentNode.parentNode;
    let cate_id = site_list.getAttribute("data-id");
    tr_dom.setAttribute('date-cate-id', cate_id);
    let tbody = site_list.getElementsByTagName('tbody')[0];
    tbody.appendChild(tr_dom)
}

function save_new_website(e) {
    console.log(e);
    let tr_dom = e.target.closest('tr');
    let input_doms = tr_dom.getElementsByTagName('input');
    let name_input_dom = tr_dom.getElementsByClassName('name-cel')[0];
    let url_input_dom = tr_dom.getElementsByClassName('url-cel')[0];
    let order_input_dom = tr_dom.getElementsByClassName('order-cel')[0];

    if (!input_valid(input_doms)) {
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
