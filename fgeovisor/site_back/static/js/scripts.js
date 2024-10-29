function initMap() {
    var southWest = L.latLng(-85.0511287798, -180),
        northEast = L.latLng(85.0511287798, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    var map = L.map('map', {
        editable: true,//Включаем пакет, позволяющий производить редактирование объектов leaflet
        attributionControl: false,//отключаем ссылку на нытьё хохла
        maxBounds: bounds,
        maxBoundsViscosity: 1.0,
        minZoom: 3,
        zoomControl: false
    }).setView([45.03, 41.96], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);


    //подгрузка полигонов из БД

    getPolygons();

    function getPolygons(){
        fetch("get-polygons/")
            .then(function(response){
            return response.json();
            })
            .then(function(data){
                displayPolygons(data);
            })
    }

    //Массив с полигонами, нужен для корректного отображения полигонов при работе с ними
    let polygonLayerGroup  = L.layerGroup().addTo(map);

    function toggleButtonDisplay(createVisible, finishVisible, cancelVisible) {
        document.getElementById("createButton").style.display = createVisible ? "block" : "none";
        document.getElementById("finishButton").style.display = finishVisible ? "block" : "none";
        document.getElementById("cancelButton").style.display = cancelVisible ? "block" : "none";
    }

    //Функция для редактирования полигонов
    function enableEdit(layer){
        layer.enableEdit(); //включаем редактирование для элемента
        layer.closePopup();// закрываемвсплывающее окно
        //проводим манипуляции с кнопками в првой части экрана
        toggleButtonDisplay(false, true, true);

        //назначаем кнопкам функции
        document.getElementById("finishButton").onclick = function(){
            finishEdit(layer);
        };
        document.getElementById("cancelButton").onclick = function(){
            cancelEdit(layer);
            getPolygons();
        };

        //функция для применения изменений
        function finishEdit(layer){
            //выключаем редактирование
            layer.disableEdit();
            //фиксируем изменения как новый полигон и удаляем старый
            console.log(layer.id)
            updatePolygon(layer);
            toggleButtonDisplay(true, false, false);
        }

        //функция  отмены изменений
        function cancelEdit(layer){
            toggleButtonDisplay(true, false, false);
            layer.disableEdit();
        }
    };

    //Функция рассчёта NDVI

    function calcNdvi(layer){
        /*fetch('calc-NDVI/',{
            method: 'Post',
            headers:{
                'content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(layer.id)
        })
        .then(function(response){
    
        })
        .catch(function(error){
    
        })*/
       alert("Функция в разработке!")
    }
    
    function calculatePolygonArea(latlngs) {
        let area = 0;
        const radius = 6371228; // Радиус Земли в метрах
    
        // Проходимся по всем точкам полигона
        for (let i = 0; i < latlngs.length; i++) {
            // Текущая точка
            const p1 = latlngs[i];
            // Следующая точка, если текущая - последняя, берем первую точку, чтобы замкнуть полигон
            const p2 = latlngs[(i + 1) % latlngs.length];
            
            // Преобразуем широту точек из градусов в радианы
            const lat1 = p1.lat * Math.PI / 180;
            const lat2 = p2.lat * Math.PI / 180;
            // Преобразуем разницу долгот между двумя соседними точками в радианы
            const deltaLng = (p2.lng - p1.lng) * Math.PI / 180;
            
            // Добавляем к общей площади слагаемое, зависящее от разности долгот и широт точек для вычисления площади на сфере
            area += (deltaLng) * (2 + Math.sin(lat1) + Math.sin(lat2));
        }
    
        area = Math.abs((area * radius * radius / 2.0) / 10000);
        return area; // Площадь в квадратных метрах
    }

    //функция отображения политгонов из БД
    function displayPolygons(geojsonData){
        //очищаем слой полигонов во избежание фатомных элементов
        polygonLayerGroup.clearLayers();
        //Создаём полигон по заданным в файле параметрам
        L.geoJSON(geojsonData,{
            style: function(){
                return {color:"deepskyblue"}
            },
            //для каждого элемента в файле JSON выполняем блок:
            onEachFeature:function(feature,layer){
                if (feature.properties && feature.id){
                    layer.id = feature.id;
                    
                    // Расчет площади
                    const latlngs = layer.getLatLngs()[0]; // Предполагается, что у нас только один полигон (без дыр)
                    const area = calculatePolygonArea(latlngs);

                    //начало блока всплывающего окна
                    let popupContent = document.createElement('div');
                    popupContent.appendChild(document.createTextNode("Это поле."));
                    
                    // Добавляем площадь в popup
                    let areaText = document.createElement('p');
                    areaText.textContent = `Площадь: ${area.toFixed(2)} га`;
                    popupContent.appendChild(areaText);

                    // Добавляем кнопки calcNdvi, deleteButton и editButton в popup
                    let calcNDVI = document.getElementById('calcNdvi').cloneNode(true);
                    calcNDVI.id='calcNdviClone';
                    popupContent.appendChild(calcNDVI);
                    calcNDVI.addEventListener("click",function(){
                        calcNdvi(layer);
                    });
                    
                    let deleteB = document.getElementById('deleteButton').cloneNode(true);
                    deleteB.id='deleteBClone';
                    deleteB.addEventListener("click", function() {
                        deletePolygon(layer);
                    });

                    let editB = document.getElementById("editButton").cloneNode(true);
                    editB.id = "editBClone";
                    editB.addEventListener("click", function(){
                        enableEdit(layer);
                    })
                    popupContent.appendChild(deleteB);
                    popupContent.appendChild(editB);
                    layer.bindPopup(popupContent);
                    //конец блока всплывающего окна
                }
            }
            //добавляем полигон на слой
        }).addTo(polygonLayerGroup);
    }

    //удаление полигона
    function deletePolygon(layer){
        fetch('delete-polygon/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Добавляем CSRF-токен
            },
            body: JSON.stringify(layer.id)
        })
        .then(function(response) { //перехват респонса из джанго
            return response.json();
        })
        .then(function(data) {
            console.log('Success:', data);
            layer.remove();

        })
        .catch(function(error) {
            console.error('Error:', error);
        });
    }
    
    //функция создания полигона
    function createPolygon(){
        //манипуляции с кнопками в правой части экрана
        toggleButtonDisplay(false, true, true);

        //создание пустого полигона и линий предпросмотра
        let latLng = [];
        let newfield = L.polygon(latLng, { color: 'deepskyblue', dashArray: "10, 5" }).addTo(map);
        let tempLine = L.polyline([],{color:'gray',dashArray: "10, 5"}).addTo(map);
        

        // Меняем курсор при старте создания полигона
        map.getContainer().style.cursor = 'crosshair';

        //добавляем обработчик для кликов
         function onMapClick(e) {
            // Добавляем координаты клика в массив
            latLng.push(e.latlng); 
            // Обновляем полигон с новыми координатами
            newfield.setLatLngs(latLng); 
            //задаём точку для линии предпросмотра
            tempLine.setLatLngs([e.latLng,e.latLng]);
        }

        //функция обработчика движения мышкой
        function onMapMouseMove(e){
            //начинаем предпросмотр, если есть хотябы 1 точка
            if (latLng.length > 0){
                tempLine.setLatLngs([latLng[latLng.length - 1], e.latlng]);
            }
            //в случае двух, если есть хотя-бы 2 точки, ведём линию ещё и к первой
            if (latLng.length > 1){
                tempLine.setLatLngs([latLng[latLng.length - 1], e.latlng, latLng[0]]);
            }
        }

        // Включаем обработчик кликов
        map.on('click', onMapClick); 
        //включаем обработчик движения мышью
        map.on('mousemove', onMapMouseMove);

        //добавляем кнопке "Применить" функционал
        document.getElementById("finishButton").onclick = function() {
            //если у полигона больше 2 точек
            if (latLng.length >= 3){
                //убираем пунктир у границ полигона
                const newStyle = {dashArray: "0, 0"};
                newfield.setStyle(newStyle);
                // Отключаем обработчик кликов
                map.off('click', onMapClick);
                //Выключиие обработчика движения мыши
                map.off('mousemove',onMapMouseMove);
                // Возвращаем курсор в исходное состояние
                map.getContainer().style.cursor = ''; 
                //манипулируем кнопками на правой панели
                toggleButtonDisplay(true, false, false);
                //формируем json
                let geojson = newfield.toGeoJSON();
                //отправляем json в django
                savePolygon(geojson);
                //удаляем локальный полигон и линии предпросмотра
                newfield.remove();
                tempLine.remove();
            }else{
                //если у полигона меньше 3х точек
                alert("У поля должно быть минимум 3 угла!")
            }
        };
        
        //добавляем функционал кнопке отмены
        document.getElementById("cancelButton").onclick = function(){
            //выключаем обработчик кликов
            map.off('click', onMapClick);
            //выключаем обработчик движения мышью
            map.off('mousemove',onMapMouseMove);
            //возвращаем курсор в исходное состояние
            map.getContainer().style.cursor = '';
            //манипулируем кнопками в правой части экрана
            toggleButtonDisplay(true, false, false);
            //удаляем поле и линии предпросмотра
            newfield.remove();
            tempLine.remove();
        }
    }

    //добавляем функцию кнопке "Создать"
    document.getElementById("createButton").onclick = function(){
        createPolygon();
    }

    //функция обновления полигона
    async function updatePolygon(layer) {
        data = {
            LatLngs: layer.getLatLngs(),
            id: layer.id
        };
        console.log (JSON.stringify(data))
        fetch('updete-polygon/',{
            method: 'POST',
            headers:{
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(function(response){
            return response.json();
        });
        await delay(200);
        console.log("обновляем полигоны");
        getPolygons();
    }

    //Функция сохранения полигона
    async function savePolygon(geojson){
        fetch('create-polygon/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Добавляем CSRF-токен
            },
            body: JSON.stringify(geojson)
        })
        .then(function(response) { //перехват респонса из джанго
            return response.json();
        })
        .then(function(data) {
            console.log('Success:', data);
        })
        .catch(function(error) {
            console.error('Error:', error);
        });
        await delay(200);
        console.log("обновляем полигоны");
        getPolygons();
    }
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

//Инициализация карты при загрузке страницы
document.addEventListener("DOMContentLoaded", function() {
    initMap();
    bindValidation();
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
    bulling();
    switchsidebarcontent();
});