// Функция для привязки валидации пароля
export function bindValidation() {
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
export function bulling(){
    if (window.permition_access == "True"){
        alert("Куда ты лезешь?!");
    }
}

//Задержки
export function delay(ms){
    return new Promise(function(resolve){
        setTimeout(resolve,ms);
    })
}