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


function showProgressBar() { 
    return new Promise((resolve) => {
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');

        // Показываем прогресс-бар
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';

        let progress = 0;
        const interval = setInterval(() => {
            progress += 10; // Увеличиваем прогресс каждые 400 мс
            progressBar.style.width = progress + "%";

            if (progress >= 100) {
                clearInterval(interval);
                // Скрываем прогресс-бар через 1 секунду после завершения
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    resolve(); // Уведомляем, что прогресс-бар завершён
                }, 1000);
            }
        }, 400);
    });
}