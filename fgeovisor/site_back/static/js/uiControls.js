function toggleButtonDisplay(createVisible, finishVisible, cancelVisible) {
    document.getElementById("createButton").style.display = createVisible ? "block" : "none";
    document.getElementById("finishButton").style.display = finishVisible ? "block" : "none";
    document.getElementById("cancelButton").style.display = cancelVisible ? "block" : "none";
}

// Функция для переключения бокового меню

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.style.width = sidebar.style.width === "250px" ? "0" : "250px";
}

// Функция для открытия модального окна

function openModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "block"; // Показываем модальное окно
}

// Функция для закрытия модального окна

function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none"; // Скрываем модальное окно
    document.getElementById("modalBody").innerHTML = ""; // Очищаем содержимое модального окна
    loginerror = "False"
    regerror = "False"
}

// Функция для отображения формы входа

function showLoginForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("loginForm").innerHTML; // Загружаем содержимое формы входа
    if (loginerror == "True"){
        document.getElementById("errormsg").style.display = "block";
    }
    openModal(); // Открываем модальное окно
    var passwordField = document.querySelectorAll("#modalBody input[type='password']");
    passwordField.forEach(function(field){
        field.style.width = "100%"; // Изменяем ширину поля ввода пароля
    });
}

// Функция для отображения формы регистрации

function showRegistrationForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("registrationForm").innerHTML; // Загружаем содержимое формы регистрации
    if (regerror == "True"){
        document.getElementById("errorrg").style.display = "block";
    }
    openModal(); // Открываем модальное окно
    var form = document.querySelector("form[action]");
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

//Смена бокового меню для пользователя

function switchsidebarcontent(){
    if (authcheck == "False"){
        document.getElementById("createButton").style.display = "none";
        document.getElementById("loggedinbuttons").style.display = "none";
        document.getElementById("defoltview").style.display = "block";
    }else{
        document.getElementById("loggedinbuttons").style.display = "block";
        document.getElementById("defoltview").style.display = "none";
        if (isadmin == "False"){
            document.getElementById("superuser").style.display = "none";
        }else{
            document.getElementById("superuser").style.display = "block";
        }
    }
    if (loginerror == "True"){
        showLoginForm();
    }
    if (regerror == "True"){
        showRegistrationForm();
    }
}