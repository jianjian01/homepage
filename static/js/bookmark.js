function bookmark_request(action, url, data, onSuccess) {
    let main = document.getElementById('main-bookmark');
    let request = new XMLHttpRequest();
    request.open(action, url, true);
    request.addEventListener('load', function () {
        let result = {};
        try {
            result = JSON.parse(request.responseText);
        } catch (e) {
        }
        if (request.status >= 200 && request.status < 300 && result.status === 1) {
            onSuccess();
            return;
        }
        alert(result.message || main.dataset.requestFailed);
    });
    request.addEventListener('error', function () {
        alert(main.dataset.requestFailed);
    });
    data.set('csrf_token', document.head.querySelector('[name~=csrf-token][content]').content);
    request.send(data);
}

function open_bookmark_modal(action, url, title, values) {
    let form = document.getElementById('bookmark-form');
    form.reset();
    form.dataset.action = action;
    form.dataset.url = url;
    document.getElementById('bookmark-modal-title').innerText = title;
    if (values) {
        form.elements.title.value = values.title;
        form.elements.url.value = values.url;
        form.elements.tags.value = values.tags;
    }
    $('#bookmark-modal').modal('show');
}

function add_bookmark() {
    let main = document.getElementById('main-bookmark');
    open_bookmark_modal('POST', '/bookmarks/', main.dataset.addTitle);
}

function edit_bookmark(event) {
    let main = document.getElementById('main-bookmark');
    let item = event.target.closest('.bookmark-item');
    open_bookmark_modal('PUT', '/bookmarks/' + item.dataset.id, main.dataset.editTitle, item.dataset);
}

function save_bookmark(event) {
    event.preventDefault();
    let form = event.target;
    if (!form.reportValidity()) {
        return;
    }
    let isCreate = form.dataset.action === 'POST';
    bookmark_request(form.dataset.action, form.dataset.url, new FormData(form), function () {
        if (isCreate) {
            window.location = '/?view=bookmarks';
        } else {
            refresh();
        }
    });
}

function delete_bookmark(event) {
    let main = document.getElementById('main-bookmark');
    if (!window.confirm(main.dataset.confirmDelete)) {
        return;
    }
    let item = event.target.closest('.bookmark-item');
    bookmark_request('DELETE', '/bookmarks/' + item.dataset.id, new FormData(), refresh);
}

document.getElementById('btn-add-bookmark').addEventListener('click', add_bookmark);
document.getElementById('bookmark-form').addEventListener('submit', save_bookmark);
for (let button of document.getElementsByClassName('edit-bookmark')) {
    button.addEventListener('click', edit_bookmark);
}
for (let button of document.getElementsByClassName('delete-bookmark')) {
    button.addEventListener('click', delete_bookmark);
}
