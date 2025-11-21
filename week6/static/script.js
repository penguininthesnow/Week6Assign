window.addEventListener("DOMContentLoaded", () =>{
    const form = document.getElementById("loginForm");
    const checkbox = document.getElementById("agreeBox");

    form.addEventListener("submit", function (event) {
        if(!checkbox.checked) {
            event.preventDefault(); // 表單無法送出
            alert("請勾選同意條款");
        }
    });
});