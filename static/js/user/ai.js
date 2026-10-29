document.getElementById('ai-config-form').addEventListener('submit', function (event) {
    event.preventDefault();
    let form = event.target;
    if (!form.reportValidity()) {
        return;
    }
    let main = document.getElementById('main-ai');
    let status = document.getElementById('ai-config-status');
    let data = new FormData(form);
    data.set('csrf_token', document.head.querySelector('[name~=csrf-token][content]').content);
    let request = new XMLHttpRequest();
    request.open('PUT', form.action, true);
    request.addEventListener('load', function () {
        let result = {};
        try {
            result = JSON.parse(request.responseText);
        } catch (e) {
        }
        if (request.status >= 200 && request.status < 300 && result.status === 1) {
            form.elements.api_key.value = '';
            status.className = 'ml-2 text-success';
            status.innerText = main.dataset.saveSuccess;
            return;
        }
        status.className = 'ml-2 text-danger';
        status.innerText = result.message || main.dataset.requestFailed;
    });
    request.addEventListener('error', function () {
        status.className = 'ml-2 text-danger';
        status.innerText = main.dataset.requestFailed;
    });
    request.send(data);
});
