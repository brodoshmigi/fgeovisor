var savedTheme = localStorage.getItem('theme');

export function toggleButtonDisplay(createVisible, finishVisible, cancelVisible) {
    document.getElementById("createButton").style.display = createVisible ? "block" : "none";
    document.getElementById("finishButton").style.display = finishVisible ? "block" : "none";
    document.getElementById("cancelButton").style.display = cancelVisible ? "block" : "none";
}

window.toggleButtonDisplay = toggleButtonDisplay;

// Функция для переключения бокового меню

export function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menuButton");
    sidebar.style.width = sidebar.style.width === "250px" ? "0" : "250px";
    if (savedTheme){
        if (savedTheme === "light"){
            menuButton.style.border = sidebar.style.width === "250px" ? "0px solid #20bab0" : "1px solid #20bab0";
        }else{
            menuButton.style.border = "0px solid #20bab0";
            menuButton.style.boxShadow = sidebar.style.width === "250px" ? "none" : "0 2px 5px rgba(0, 0, 0, 0.3)"
        }
    }
}

window.toggleSidebar = toggleSidebar;

// Функция для открытия модального окна

function openModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "block"; // Показываем модальное окно
    modal.addEventListener("click", handleOutsideClick);
}

// Функция для закрытия модального окна

export function closeModal() {
    const modal = document.getElementById("modal");
    modal.style.display = "none"; // Скрываем модальное окно
    document.getElementById("modalBody").innerHTML = ""; // Очищаем содержимое модального окна
    loginerror = "False"
    regerror = "False"
    modal.removeEventListener("click", handleOutsideClick);
}

window.closeModal = closeModal;

function handleOutsideClick(event){
    const modalContent = document.getElementById("modal-content");
    if (!modalContent.contains(event.target)){
        closeModal();
    }
}

// Функция для отображения формы входа

export function showLoginForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("loginForm").innerHTML; // Загружаем содержимое формы входа
    const modal = document.getElementById("modal-content");
    modal.style.width = "700px";
    modal.style.height = "350px";
    if (loginerror == "True"){
        document.getElementById("errormsg").style.display = "block";
    }
    openModal(); // Открываем модальное окно
    var passwordField = document.querySelectorAll("#modalBody input[type='password']");
    passwordField.forEach(function(field){
        field.style.width = "100%"; // Изменяем ширину поля ввода пароля
    });
}

window.showLoginForm = showLoginForm;

// Функция для отображения формы регистрации

export function showRegistrationForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("registrationForm").innerHTML; // Загружаем содержимое формы регистрации
    if (regerror == "True"){
        document.getElementById("errorrg").style.display = "block";
    }
    const modal = document.getElementById("modal-content");
    modal.style.width = "700px";
    modal.style.height = "350px";
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

window.showRegistrationForm = showRegistrationForm;

//Смена бокового меню для пользователя

export function switchsidebarcontent(){
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
        document.getElementById('ui-button').style.display = "block";
    }
    if (loginerror == "True"){
        showLoginForm();
    }
    if (regerror == "True"){
        showRegistrationForm();
    }
}

// темы и всё, что с ними связано

export function switchTheme(themChoose) {
    const themeLink = document.getElementById('theme');
    if (themChoose === "dark"){
        themeLink.setAttribute("href",staticUrls.dark);
        localStorage.setItem('theme','dark');
        savedTheme = "dark";
    }else{
        themeLink.setAttribute("href",staticUrls.light);
        localStorage.setItem('theme','light');
        savedTheme = "light";
    }
}

window.switchTheme = switchTheme;

export function autoSwitchTheme() {
    const themeLink = document.getElementById('theme');
    const savedTheme = localStorage.getItem('theme');
    const savedColor = localStorage.getItem('selectedColor');
    if (savedTheme) {
        if (savedTheme === 'dark') {
            themeLink.setAttribute('href', staticUrls.dark);
        } else {
            themeLink.setAttribute('href', staticUrls.light);
        }
    } else {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            themeLink.setAttribute('href', staticUrls.dark);
        } else {
            themeLink.setAttribute('href', staticUrls.light);
        }
    }
    if (savedColor) {
        polygonLayerGroup.eachLayer(function(layer) {
            layer.setStyle({ color: savedColor });
        });

        const colorLink = document.getElementById('colors');
        colorLink.setAttribute('href', staticUrls[savedColor]);
    }
}


window.autoSwitchTheme = autoSwitchTheme;

export function switchColor(color) {
    const colorLink = document.getElementById('colors');
    let selectedColor;
    if (color === "blue") {
        colorLink.setAttribute("href", staticUrls.deepskyblue);
        selectedColor = "deepskyblue";
    } else if (color === "red") {
        colorLink.setAttribute("href", staticUrls.crimson);
        selectedColor = "crimson";
    } else if (color === "gold") {
        colorLink.setAttribute("href", staticUrls.gold);
        selectedColor = "gold";
    } else if (color === "purple") {
        colorLink.setAttribute("href", staticUrls.blueviolet);
        selectedColor = "blueviolet";
    }
    polygonLayerGroup.eachLayer(function(layer) {
        layer.setStyle({ color: selectedColor });
    });
    localStorage.setItem('selectedColor', selectedColor);
}

window.switchColor = switchColor;

export function showThemeSettings(){
    document.getElementById("modalBody").innerHTML = document.getElementById("themeSettings").innerHTML;
    const modal = document.getElementById("modal-content");
    modal.style.width = "350px";
    modal.style.height = "auto";
    openModal();
}

window.showThemeSettings = showThemeSettings;