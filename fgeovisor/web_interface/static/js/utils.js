// Функция для привязки валидации пароля
function bindValidation() {
    var form = document.querySelector("form[action]");
    if (form) {
        form.addEventListener("submit", function(event) {
            var password = document.getElementById("regPassword").value;
            var confirmPassword = document.getElementById("passwordConfirmation").value;
            if (password !== confirmPassword) {
                alert("Пароли не совпадают!");
                // Предотвращаем отправку формы
                event.preventDefault();
            }
        });
    }
}

//функция для тех, кто открывает запрещённые разделы
function bulling(){
    if (permition_access == "True"){
        alert("Куда ты лезешь?!");
    }
}

//Задержки
function delay(ms){
    return new Promise(function(resolve){
        setTimeout(resolve,ms);
    })
}

function progressBar(){
    let progressBar = document.getElementById("progress-container");
    let duration = 4200;
    let intervalTime = 20;
    let steps = duration/intervalTime;
    let increment = 100/steps
    let width = 0;
    progressBar.style.display = "block";
    let interal = setInterval(() => {
        if (width < 100){
            width += increment;
            progressBar.style.width = width + "%"
        }else {
            clearInterval(interal)
        }
    }, intervalTime)
}