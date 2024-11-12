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

// функция отображения политгонов из БД

function displayPolygons(geojsonData){
    // очищаем слой полигонов во избежание фатомных элементов
    polygonLayerGroup.clearLayers();
    // создаём полигон по заданным в файле параметрам
    L.geoJSON(geojsonData,{
        style: function(){
            return {color:"deepskyblue"}
        },
        //для каждого элемента в файле JSON выполняем блок:
        onEachFeature:function(feature,layer){
            if (feature.properties && feature.id){
                layer.id = feature.id;
                
                // расчет площади
                const latlngs = layer.getLatLngs()[0]; // предполагается, что у нас только один полигон (без дыр)
                const area = calculatePolygonArea(latlngs);

                // начало блока всплывающего окна
                let popupContent = document.createElement('div');
                popupContent.className = "popup-content"
                popupContent.appendChild(document.createTextNode("Это поле."));
                
                // добавляем площадь в popup
                let areaText = document.createElement('p');
                areaText.textContent = `Площадь: ${area.toFixed(2)} га`;
                popupContent.appendChild(areaText);

                // добавляем кнопки calcNdvi, deleteButton и editButton в popup
                let calcNDVI = document.getElementById('calcNdvi').cloneNode(true);
                calcNDVI.id='calcNdviClone';
                popupContent.appendChild(calcNDVI);
                calcNDVI.addEventListener("click",function(){
                    calcNdvi(layer);
                });
                
                let uploadB = document.getElementById('uploadButton').cloneNode(true);
                uploadB.id = 'uploadBClone';

                // Поля для выбора файлов
                const fileInput1 = document.createElement('input');
                fileInput1.type = "file";
                fileInput1.accept = ".tif, .tiff, .jpg, .jpeg, .png, .geojson";
                fileInput1.style.display = "none";

                const fileInput2 = document.createElement('input');
                fileInput2.type = "file";
                fileInput2.accept = ".tif, .tiff, .jpg, .jpeg, .png, .geojson";
                fileInput2.style.display = "none";

                // Добавляем обработчики для выбора файлов
                uploadB.addEventListener("click", () => {
                    // Открываем выбор первого файла
                    fileInput1.click();
                });

                fileInput1.addEventListener("change", () => {
                    // Открываем выбор второго файла после выбора первого
                    fileInput2.click();
                });

                fileInput2.addEventListener("change", async function() {
                    const file1 = fileInput1.files[0];
                    const file2 = fileInput2.files[0];

                    if (!file1 || !file2) {
                        alert("Ошибка, выберите два изображения для загрузки.");
                        return;
                    }

                    const formData = new FormData();
                    formData.append("id", layer.id);
                    formData.append('image1', file1);
                    formData.append('image2', file2);
                    
                    console.log(formData);
                    try {
                        const response = await fetch("upload-img/", {
                            method: "POST",
                            headers: {
                                'X-CSRFToken': csrfToken,
                            },
                            body: formData,
                        });

                        if (response.ok) {
                            const result = await response.json();
                            console.log(result);
                        } else {
                            alert("Ошибка при загрузке изображений.");
                        }
                    } catch (error) {
                        console.error("Ошибка:", error);
                    }
                });

                popupContent.appendChild(uploadB);
                popupContent.appendChild(fileInput1);
                popupContent.appendChild(fileInput2);
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
                popupContent.appendChild(uploadB);
                layer.bindPopup(popupContent);
                //конец блока всплывающего окна
            }
        }
        //добавляем полигон на слой
    }).addTo(polygonLayerGroup);
}

//удаление полигона
function deletePolygon(layer){
    data = {
        'id': layer.id
    };
    fetch('delete-polygon/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Добавляем CSRF-токен
        },
        body: JSON.stringify(data)
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
        if (latLng.length >= 3 && latLng.length < 21){
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
        }else if (latLng.length > 20){
            //если у полигона больше 20 точек
            alert("У поля должно быть меньше 20 углов!")
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
async function updatePolygon(geojson) {
    fetch('update-polygon/',{
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(geojson)
    })
    .then(function(response){
        return response.json();
    })
    .then(function(data) {
        console.log('Success:', data);
    })
    await delay(50);
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
    await delay(50);
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
        geojson = layer.toGeoJSON();
        updatePolygon(geojson);
        toggleButtonDisplay(true, false, false);
    }

    //функция  отмены изменений
    function cancelEdit(layer){
        toggleButtonDisplay(true, false, false);
        layer.disableEdit();
    }
};