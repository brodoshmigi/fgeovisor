function initMap() {
    var southWest = L.latLng(-85.0511287798, -180),
        northEast = L.latLng(85.0511287798, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    var map = L.map('map', {
        attributionControl: false,
        maxBounds: bounds,
        maxBoundsViscosity: 1.0,
        minZoom: 3,
        zoomControl: false
    }).setView([45.03, 41.96], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    function createpoligon(){
        document.getElementById("createbutton").style.display = "none"
        document.getElementById("finishButton").style.display = "block"
        document.getElementById("cancelButton").style.display = "block"
        let latLng = [];
        let newfield = L.polygon(latLng, { color: 'deepskyblue', dashArray: "10, 5" }).addTo(map);
        

        // Меняем курсор при старте создания полигона
        map.getContainer().style.cursor = 'crosshair';

         function onMapClick(e) {
            latLng.push(e.latlng); // Добавляем координаты клика в массив
            newfield.setLatLngs(latLng); // Обновляем полигон с новыми координатами
        }

        map.on('click', onMapClick); // Включаем обработчик кликов

        document.getElementById("finishButton").onclick = function() {
            if (latLng.length >= 3){
                const newStyle = {dashArray: "0, 0"};
                newfield.setStyle(newStyle);
                map.off('click', onMapClick); // Отключаем обработчик кликов
                map.getContainer().style.cursor = ''; // Возвращаем курсор в исходное состояние
                document.getElementById("finishButton").style.display = "none"
                document.getElementById("cancelButton").style.display = "none"
                document.getElementById("createbutton").style.display = "block"
                //начало блока с попапами//
                let popupContent = document.createElement('div');
                let calcNDVI = document.getElementById('calcNdvi').cloneNode(true);
                calcNDVI.id='calcNdviClone';
                popupContent.appendChild(document.createTextNode("Это поле"));
                popupContent.appendChild(calcNDVI);
                newfield.bindPopup(popupContent);  //присвоение попапа 
                //конец юлока с попапами
                savePolygon(latLng);
            }else{
                alert("У поля должно быть минимум 3 угла!")
            }
        };
        
        document.getElementById("cancelButton").onclick = function(){
            map.off('click', onMapClick);
            map.getContainer().style.cursor = '';
            document.getElementById("finishButton").style.display = "none"
            document.getElementById("cancelButton").style.display = "none"
            document.getElementById("createbutton").style.display = "block"
            newfield.remove();
        }
    }

    document.getElementById("createbutton").onclick = function(){
        createpoligon();
    }


    function savePolygon(latLng){
        const data ={
            latLng: latLng.map(function(point){
                return [point.lat, point.lng];
            })
        };
        fetch('/save_polygon',{
            method: 'POST',
            headers: {
                'Content-Type':application/JSON,
                'X-CSRFToken':csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(function(response){
            return response.json();
        })
    }
}


function calcNDVI(){
    alert("1334");
}

document.addEventListener("click", function(event){
    if (event.target && event.target.id.startsWith("calcNdviClone")){
        calcNDVI();
    }
})

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
}

// Функция для отображения формы входа
function showLoginForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("loginForm").innerHTML; // Загружаем содержимое формы входа
    openModal(); // Открываем модальное окно
    var passwordField = document.querySelectorAll("#modalBody input[type='password']");
    passwordField.forEach(function(field){
        field.style.width = "100%"; // Изменяем ширину поля ввода пароля
    });
}

// Функция для отображения формы регистрации
function showRegistrationForm() {
    document.getElementById("modalBody").innerHTML = document.getElementById("registrationForm").innerHTML; // Загружаем содержимое формы регистрации
    openModal(); // Открываем модальное окно
    var form = document.querySelector("form[action]");
    form.addEventListener("submit", function(event) {
        var password = document.getElementById("regPassword").value;
        var confirmPassword = document.getElementById("passwordConfirmation").value;
        if (password !== confirmPassword) {
            alert("Пароли не совпадают!");
            event.preventDefault(); // Предотвращаем отправку формы
        }
    });
}

// Функция для привязки валидации пароля
function bindValidation() {
    var form = document.querySelector("form[action]");
    if (form) {
        form.addEventListener("submit", function(event) {
            var password = document.getElementById("regPassword").value;
            var confirmPassword = document.getElementById("passwordConfirmation").value;
            if (password !== confirmPassword) {
                alert("Пароли не совпадают!");
                event.preventDefault(); // Предотвращаем отправку формы
            }
        });
    }
}

// функция для создания полигонов


//Инициализация карты при загрузке страницы
document.addEventListener("DOMContentLoaded", function() {
    initMap();
    bindValidation();
    function switchsidebarcontent(){
        if (authcheck == "False"){
            document.getElementById("createbutton").style.display = "none";
            document.getElementById("loggedinbuttons").style.display = "none";
            document.getElementById("defoltview").style.display = "block";
        }else{
            document.getElementById("loggedinbuttons").style.display = "block";
            document.getElementById("defoltview").style.display = "none";
        }
    }
    switchsidebarcontent();
});