 //Функция рассчёта NDVI

 function calcNdvi(layer, del) {
    var layerID = 'ndviLayer_' + layer.id;
    var isPhotoRendered = map._layers[layerID];
    var ndviValueDisplay; // Объявляем переменную на уровне функции

    if (del === true) {
        return new Promise((resolve) => {
            if (isPhotoRendered) {
                map.removeLayer(isPhotoRendered);
            }
            resolve();
        });
    } else {
        if (isPhotoRendered) {
            map.removeLayer(isPhotoRendered);
            layer.setStyle({
                fillOpacity: 0.5 // Полупрозрачный полигон
            });
            delete map._layers[layerID];
        } else {
            latlngBounds = layer.getLatLngs();
            const requestURL = '/get-img/' + layer.id;
            fetch(requestURL, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Добавляем CSRF-токен
                }
            })
            .then(response => response.json())
            .then(data => {
                const { id, url } = data;
                layer.setStyle({
                    fillOpacity: 0 // Полупрозрачный полигон
                });

                // Создаем слой NDVI и добавляем его на карту
                var ndviLayer = L.imageOverlay(url, latlngBounds);
                ndviLayer.addTo(map);
                map._layers[layerID] = ndviLayer;

                // Создаем элемент для отображения значения NDVI
                ndviValueDisplay = L.DomUtil.create('div', 'ndvi-value-display');
                document.body.appendChild(ndviValueDisplay);

                // Обработчик события mousemove на полигоне
                layer.on('mousemove', function (e) {
                    if (!ndviValueDisplay) {
                        console.error("ndviValueDisplay не определен");
                        return;
                    }

                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');
                    var img = new Image();
                    img.crossOrigin = "Anonymous";
                    img.src = url;

                    img.onload = function () {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0, img.width, img.height);

                        // Преобразуем координаты курсора в координаты изображения
                        var bounds = ndviLayer.getBounds();
                        var pixelX = Math.floor(((e.latlng.lng - bounds.getWest()) / (bounds.getEast() - bounds.getWest())) * img.width);
                        var pixelY = Math.floor(((bounds.getNorth() - e.latlng.lat) / (bounds.getNorth() - bounds.getSouth())) * img.height);

                        // Получаем цвет пикселя
                        var pixel = ctx.getImageData(pixelX, pixelY, 1, 1).data;

                        var ndviValue = calculateNDVI(pixel[0], pixel[1], pixel[2]);

                        // Отображаем значение NDVI рядом с курсором
                        var point = e.containerPoint; // Получаем координаты мыши относительно контейнера карты
                        ndviValueDisplay.style.left = point.x + 10 + 'px';
                        ndviValueDisplay.style.top = point.y + 10 + 'px';
                        ndviValueDisplay.textContent = 'NDVI: ' + ndviValue.toFixed(2);
                    };

                    img.onerror = function () {
                        console.error("Ошибка загрузки изображения NDVI");
                    };
                });

                // Обработчик события mouseout на полигоне
                layer.on('mouseout', function () {
                    if (ndviValueDisplay) {
                        ndviValueDisplay.textContent = '';
                    }
                });
            });
        }
    }
}


// Функция для вычисления NDVI на основе RGB 
// !!! Переписать !!!
function calculateNDVI(r, g, b) {
    var nir = r;
    var red = b;
    var ndvi = (nir - red) / (nir + red);
    if (ndvi < 0){
        ndvi = 0;
    }
    return ndvi;
}


//Функция рассчёта площади поля

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