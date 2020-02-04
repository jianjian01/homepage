function add_new_rss(e) {
    let rss_dom = document.getElementById('main-rss');
    let tbody = rss_dom.getElementsByTagName('tbody');
    if (tbody === null) {
        return
    }
    let row = tbody[0].insertRow();
    let num_dom = document.createElement('th');
    let name_dom = document.createElement('td');
    name_dom.classList.add('new-cel');
    let name_input_dom = new_input_dom('name', 'text', 'name', true, true);
    name_input_dom.classList.add('name-cel');
    name_dom.appendChild(name_input_dom);

    let url_dom = document.createElement('td');
    url_dom.classList.add('new-cel');
    let url_input_dom = new_input_dom('name', 'url', 'https://example.com/feed', true, false);
    url_input_dom.classList.add('large-url-cel');
    url_dom.appendChild(url_input_dom);

    let action_dom = document.createElement("td");
    let action = new_save_btn();
    action.onpointerdown = save_new_cate;
    action_dom.appendChild(action);

    row.appendChild(num_dom);
    row.appendChild(name_dom);
    row.appendChild(url_dom);
    row.appendChild(action_dom);
}

function save_new_cate(e) {
    let tr_dom = e.target.closest('tr');
    let input_doms = tr_dom.getElementsByTagName('input');

    if (!input_valid(input_doms)) {
        return
    }
    let name_input_dom = tr_dom.getElementsByClassName('name-cel')[0];
    let url_input_dom = tr_dom.getElementsByClassName('large-url-cel')[0];
    let name_val = name_input_dom.value;
    let url_val = url_input_dom.value;

    let data = new FormData();
    data.append('name', name_val);
    data.append('url', url_val);

    http_request_json('POST', document.URL, data, refresh)
}

function remove_rss(e) {
    let tr_dom = e.target.closest('tr');
    let rss_id = tr_dom.getAttribute('data-id');
    let data = new FormData();
    data.append('id', rss_id);
    http_request_json('DELETE', document.URL, data, refresh)
}

function run() {
    let add_btn = document.getElementById('btn-add-rss');
    let delete_btn = document.getElementsByClassName('delete-rss');
    add_btn.onpointerdown = add_new_rss;
    for (let btn of delete_btn) {
        btn.onpointerdown = remove_rss;
    }
}

window.onload = run;