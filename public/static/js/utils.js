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

function logout(){
    fetch ('http://127.0.0.1/api/log-out/',{
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
        .then(response => {
            location.reload();
        })
}

async function login(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const data = {
        username: username,
        password: password
    };

    fetch('api/log-in/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        location.reload();
    })
}
