//Функция рассчёта NDVI
var ndviValueDisplay = null;

async function calcIndex(layer, del /*, index*/) {
    var layerID = "ndviLayer_" + layer.id;
    var isPhotoRendered = map._layers[layerID];
    var popup = document.getElementsByClassName(
        "leaflet-popup  leaflet-zoom-animated"
    );
    Array.from(popup).forEach((popup) => {
        const closeButton = popup.querySelector(".leaflet-popup-close-button");
        closeButton.click();
    });

    if (del === true) {
        return new Promise((resolve) => {
            if (isPhotoRendered) {
                layer.off("mousemove");
                layer.setStyle({ fillOpacity: 0.2 });
                delete map._layers[layerID];
                map.removeLayer(isPhotoRendered);
            }
            resolve();
        });
    } else {
        if (isPhotoRendered) {
            console.log(layer);
            layer.setStyle({
                fillOpacity: 0.2, // Полупрозрачный полигон
            });
            delete map._layers[layerID];
            layer.off("mousemove");
            layer.off("mouseout");
            map.removeLayer(isPhotoRendered);
        }
        latlngBounds = layer.getLatLngs();
        let pic_date = await window.handleCalendarClick();
        const requestURL =
            "/get-img-gee/" + layer.id + "/" + pic_date; /* + index */
        await fetch(requestURL, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken, // Добавляем CSRF-токен
            },
        }).then((response) => {
            if (response.status == 507) {
                alert("Снимка для этой даты не существует");
            } else {
                fetch("/get-img/" + layer.id + "/" + pic_date /* + index */, {
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken, // Добавляем CSRF-токен
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        const { id, url } = data;
                        layer.setStyle({
                            fillOpacity: 0, // Полупрозрачный полигон
                        });

                        // Создаем слой NDVI и добавляем его на карту
                        var ndviLayer = L.imageOverlay(url, latlngBounds);
                        ndviLayer.addTo(map);
                        map._layers[layerID] = ndviLayer;

                        // Обработчик события mousemove на полигоне
                        layer.on("mousemove", function (e) {
                            if (!ndviValueDisplay) {
                                ndviValueDisplay = L.DomUtil.create(
                                    "div",
                                    "ndvi-value-display"
                                );
                                document.body.appendChild(ndviValueDisplay);
                            }

                            var canvas = document.createElement("canvas");
                            var ctx = canvas.getContext("2d");
                            var img = new Image();
                            img.crossOrigin = "Anonymous";
                            img.src = url;

                            img.onload = function () {
                                canvas.width = img.width;
                                canvas.height = img.height;
                                ctx.drawImage(img, 0, 0, img.width, img.height);

                                // Преобразуем координаты курсора в координаты изображения
                                var bounds = ndviLayer.getBounds();
                                var pixelX = Math.floor(
                                    ((e.latlng.lng - bounds.getWest()) /
                                        (bounds.getEast() - bounds.getWest())) *
                                        img.width
                                );
                                var pixelY = Math.floor(
                                    ((bounds.getNorth() - e.latlng.lat) /
                                        (bounds.getNorth() -
                                            bounds.getSouth())) *
                                        img.height
                                );

                                // Получаем цвет пикселя
                                var pixel = ctx.getImageData(
                                    pixelX,
                                    pixelY,
                                    1,
                                    1
                                ).data;

                                var ndviValue = calculateIndex(
                                    pixel[0], // Red channel (B4)
                                    pixel[1], // Green channel (unused here, but we could use it if needed)
                                    pixel[2] // Blue channel (B2)
                                );

                                // Отображаем значение NDVI рядом с курсором
                                var point = e.containerPoint;
                                if (ndviValueDisplay) {
                                    ndviValueDisplay.style.left =
                                        point.x + 10 + "px";
                                    ndviValueDisplay.style.top =
                                        point.y + 10 + "px";
                                    ndviValueDisplay.textContent =
                                        "NDVI: " + ndviValue.toFixed(2);
                                }
                            };

                            img.onerror = function () {
                                console.error(
                                    "Ошибка загрузки изображения NDVI"
                                );
                            };
                        });

                        layer.on("mouseout", function () {
                            if (ndviValueDisplay) {
                                ndviValueDisplay.textContent = "";
                                L.DomUtil.remove(ndviValueDisplay);
                                ndviValueDisplay = null;
                            }
                        });
                    });
            }
        });
    }
}

function calculateIndex(r, g, b) {
    const keyPoints = [
        { r: 68, g: 1, b: 84, value: 0.0 }, // Фиолетовый (0)
        { r: 72, g: 35, b: 116, value: 0.1 }, //
        { r: 59, g: 82, b: 139, value: 0.2 }, //
        { r: 44, g: 114, b: 142, value: 0.3 }, //
        { r: 33, g: 144, b: 141, value: 0.4 }, //
        { r: 39, g: 173, b: 129, value: 0.5 }, //
        { r: 92, g: 200, b: 99, value: 0.6 }, //
        { r: 170, g: 220, b: 50, value: 0.7 }, //
        { r: 253, g: 231, b: 37, value: 0.8 }, //
        { r: 253, g: 231, b: 37, value: 1.0 }, // Желтый (1)
    ];

    // Находим ближайшие ключевые точки
    let minDistance1 = Infinity;
    let minDistance2 = Infinity;
    let closestPoint1 = null;
    let closestPoint2 = null;

    for (const point of keyPoints) {
        const distance = Math.sqrt(
            Math.pow(r - point.r, 2) +
                Math.pow(g - point.g, 2) +
                Math.pow(b - point.b, 2)
        );

        if (distance < minDistance1) {
            minDistance2 = minDistance1;
            closestPoint2 = closestPoint1;
            minDistance1 = distance;
            closestPoint1 = point;
        } else if (distance < minDistance2) {
            minDistance2 = distance;
            closestPoint2 = point;
        }
    }

    // Интерполяция между двумя ближайшими точками
    const distanceTotal = minDistance1 + minDistance2;
    const weight1 = 1 - minDistance1 / distanceTotal;
    const weight2 = 1 - minDistance2 / distanceTotal;

    const interpolatedValue = (
        closestPoint1.value * weight1 +
        closestPoint2.value * weight2
    ).toFixed(2);
    return parseFloat(interpolatedValue);
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
        const lat1 = (p1.lat * Math.PI) / 180;
        const lat2 = (p2.lat * Math.PI) / 180;
        // Преобразуем разницу долгот между двумя соседними точками в радианы
        const deltaLng = ((p2.lng - p1.lng) * Math.PI) / 180;

        // Добавляем к общей площади слагаемое, зависящее от разности долгот и широт точек для вычисления площади на сфере
        area += deltaLng * (2 + Math.sin(lat1) + Math.sin(lat2));
    }

    area = Math.abs((area * radius * radius) / 2.0 / 10000);
    return area; // Площадь в квадратных метрах
}
