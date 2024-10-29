//Достаём полигоны из БД
let polygonLayerGroup;
function getPolygons(){
    fetch("get-polygons/")
        .then(function(response){
        return response.json();
        })
        .then(function(data){
            displayPolygons(data);
        })
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
                popupContent.className = "popup-content"
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
    let tempLine = L.polyline([], { color: 'gray', dashArray: "10, 5" }).addTo(map);

    // Меняем курсор при старте создания полигона
    map.getContainer().style.cursor = 'crosshair';

    // Обработчик для кликов
    function onMapClick(e) {
        // Добавляем координаты клика в массив
        latLng.push(e.latlng); 
        // Обновляем полигон с новыми координатами
        newfield.setLatLngs(latLng); 
        // Задаем точку для линии предпросмотра
        tempLine.setLatLngs([e.latlng, e.latlng]); // Исправлено e.latLng на e.latlng
    }

    // Функция обработчика движения мышкой
    function onMapMouseMove(e) {
        // Начинаем предпросмотр, если есть хотя бы 1 точка
        if (latLng.length > 0) {
            tempLine.setLatLngs([latLng[latLng.length - 1], e.latlng]); // Исправлено e.latLng на e.latlng
        }
        // В случае двух, если есть хотя бы 2 точки, ведем линию ещё и к первой
        if (latLng.length > 1) {
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
    console.log(geojson);
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

//Функция для редаактирования полигонов

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