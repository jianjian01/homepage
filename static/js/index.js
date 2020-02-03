window.onload = function () {
    // 弹出登录层
    let btn = document.getElementById('header-login-button');
    let modal = document.getElementById("login-modal");
    let close = document.getElementsByClassName("close")[0];
    btn.onclick = function (e) {
        console.log("abcd");
        modal.style.display = "block";
    };
    close.onclick = function (e) {
        modal.style.display = "none";
    };
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
};