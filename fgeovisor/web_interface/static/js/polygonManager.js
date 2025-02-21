let polygonLayerGroup;
function getPolygons() {
    polygonLayerGroup.eachLayer(function (layer) {
        calcNdvi(layer, true);
    });
    if (window.authcheck === "True") {
        fetch("get-polygons/")
            .then(function (response) {
                console.log(response);
                return response.json();
            })
            .then(function (data) {
                console.log(data);
                displayPolygons(data);
            });
    }
}

// функция отображения политгонов из БД

function displayPolygons(geojsonData) {
    // очищаем слой полигонов во избежание фатомных элементов
    polygonLayerGroup.clearLayers();
    // создаём полигон по заданным в файле параметрам
    const savedColor = localStorage.getItem("selectedColor") || "#1A4F63";

    // Создаем полигон с заданным цветом
    L.geoJSON(geojsonData, {
        style: function () {
            return { color: savedColor }; // Используем сохраненный цвет
        },
        //для каждого элемента в файле JSON выполняем блок:
        onEachFeature: function (feature, layer) {
            if (feature.properties && feature.id) {
                layer.id = feature.id;
                var layerID = "ndviLayer_" + layer.id;
                if (map._layers[layerID]) {
                    layer.setStyle({
                        fillOpacity: 0,
                    });
                }
                // расчет площади
                const latlngs = layer.getLatLngs()[0]; // предполагается, что у нас только один полигон (без дыр)
                const area = calculatePolygonArea(latlngs);

                // начало блока всплывающего окна
                let popupContent = document.createElement("div");
                popupContent.className = "popup-content";

                // добавляем площадь в popup
                let areaText = document.createElement("p");
                areaText.textContent = `Площадь: ${area.toFixed(2)} га`;
                popupContent.appendChild(areaText);

                let calcB = document.getElementById("calcNDVI").cloneNode(true);
                calcB.id = "calcBClone";
                calcB.addEventListener("click", function () {
                    calcNdvi(layer, false);
                });

                let deleteB = document
                    .getElementById("deleteButton")
                    .cloneNode(true);
                deleteB.id = "deleteBClone";
                deleteB.addEventListener("click", function () {
                    deletePolygon(layer);
                });

                let editB = document
                    .getElementById("editButton")
                    .cloneNode(true);
                editB.id = "editBClone";
                editB.addEventListener("click", function () {
                    enableEdit(layer);
                });
                popupContent.appendChild(calcB);
                popupContent.appendChild(deleteB);
                popupContent.appendChild(editB);
                layer.bindPopup(popupContent);
                //конец блока всплывающего окна
            }
        },
    }).addTo(polygonLayerGroup);
}

//удаление полигона
async function deletePolygon(layer) {
    await calcNdvi(layer, true);
    const data = {
        id: layer.id,
    };
    try {
        const response = await fetch("delete-polygon/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken, // Добавляем CSRF-токен
            },
            body: JSON.stringify(data),
        });
        const result = await response.json();
        console.log("Success:");
        layer.remove();
    } catch (error) {
        console.error("Error:", error);
    }
}

//функция создания полигона
function createPolygon() {
    document.querySelectorAll(".leaflet-interactive").forEach((el) => {
        el.style.pointerEvents = "none";
    });
    if (document.querySelector(".leaflet-popup-close-button")) {
        document.querySelector(".leaflet-popup-close-button").click();
    }
    toggleButtonDisplay(false, true, true);
    const savedColor = localStorage.getItem("selectedColor") || "#1A4F63";
    let latLng = [];
    let markers = [];
    let newfield = L.polygon(latLng, {
        color: savedColor,
        dashArray: "10, 5",
    }).addTo(map);
    let tempLine = L.polyline([], { color: "gray", dashArray: "10, 5" }).addTo(
        map
    );

    map.getContainer().style.cursor = "crosshair";

    function addMarker(latlng, index) {
        let marker = L.marker(latlng, {
            icon: L.divIcon({
                className: "custom-marker",
                iconSize: [10, 10], // Размер квадрата
                html: '<div style="width:10px; height:10px; background: white;"></div>',
            }),
            draggable: false,
        }).addTo(map);

        marker.on("click", function () {
            removePoint(index);
        });

        return marker;

        // Если точка не находится внутри другого полигона, добавляем маркер
    }

    function updateMarkers() {
        markers.forEach((marker) => map.removeLayer(marker));
        markers = latLng.map((point, index) => addMarker(point, index));
    }

    function onMapClick(e) {
        latLng.push(e.latlng);
        newfield.setLatLngs(latLng);
        tempLine.setLatLngs([e.latlng, e.latlng]);
        updateMarkers();
    }

    function onMapMouseMove(e) {
        if (latLng.length > 0) {
            tempLine.setLatLngs([latLng[latLng.length - 1], e.latlng]);
        }
        if (latLng.length > 1) {
            tempLine.setLatLngs([
                latLng[latLng.length - 1],
                e.latlng,
                latLng[0],
            ]);
        }
    }

    function removePoint(index) {
        if (latLng.length > 0) {
            latLng.splice(index, 1);
            newfield.setLatLngs(latLng);
            updateMarkers();

            if (latLng.length > 1) {
                tempLine.setLatLngs([
                    latLng[latLng.length - 1],
                    map.mouseEventToLatLng(event),
                ]);
            } else {
                tempLine.setLatLngs([]);
            }
        }
    }

    function finishCreation() {
        document.removeEventListener("keydown", onKeyDown);
        let areaerr;
        let cornerr;
        if (calculatePolygonArea(latLng) / 100 > 100) {
            areaerr = "поле должно быть не более 10000 га.";
        } else {
            areaerr = null;
        }
        if (
            latLng.length >= 3 &&
            latLng.length < 51 &&
            calculatePolygonArea(latLng) / 100 < 100
        ) {
            newfield.setStyle({ dashArray: "0, 0" });
            map.off("click", onMapClick);
            map.off("mousemove", onMapMouseMove);
            document.removeEventListener("keydown", onKeyDown);
            map.getContainer().style.cursor = "";
            toggleButtonDisplay(true, false, false);
            let geojson = newfield.toGeoJSON();
            savePolygon(geojson);
            newfield.remove();
            tempLine.remove();
            markers.forEach((marker) => map.removeLayer(marker));
        } else if (latLng.length > 50) {
            cornerr = "у поля должно быт не более 50 углов";
        } else if (latLng.length < 3) {
            cornerr = "у поля должно быть не менее 3 улов";
        } else {
            cornerr = null;
        }
        if (cornerr || areaerr) {
            if (cornerr && areaerr) {
                alert(cornerr + " и " + areaerr);
            } else if (cornerr) {
                alert(cornerr);
            } else {
                alert(areaerr);
            }
        }
    }

    function onKeyDown(event) {
        if (event.key === "Backspace" || event.key === "Delete") {
            removePoint(latLng.length - 1);
        }
        if (event.key === "Enter") {
            finishCreation();
        }
    }

    map.on("click", onMapClick);
    map.on("mousemove", onMapMouseMove);
    document.addEventListener("keydown", onKeyDown);

    document.getElementById("cancelButton").onclick = function () {
        document.removeEventListener("keydown", onKeyDown);
        map.off("click", onMapClick);
        map.off("mousemove", onMapMouseMove);
        document.removeEventListener("keydown", onKeyDown);
        map.getContainer().style.cursor = "";
        toggleButtonDisplay(true, false, false);
        newfield.remove();
        tempLine.remove();
        markers.forEach((marker) => map.removeLayer(marker));
        document.querySelectorAll(".leaflet-interactive").forEach((el) => {
            el.style.pointerEvents = "auto";
        });
    };

    document.getElementById("finishButton").onclick = finishCreation;
}

//добавляем функцию кнопке "Создать"
document.getElementById("createButton").onclick = function () {
    createPolygon();
    document.getElementById("calendarWrapper").style.display = "none";
};

//функция обновления полигона
async function updatePolygon(geojson) {
    fetch("update-polygon/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(geojson),
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            console.log("Success:");
        });
    await showProgressBar();
    getPolygons();
}

//Функция сохранения полигона
async function savePolygon(geojson) {
    console.log(geojson);
    fetch("create-polygon/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken, // Добавляем CSRF-токен
        },
        body: JSON.stringify(geojson),
    })
        .then(function (response) {
            console.log(response);
            return response.json();
        })
        .then(function (data) {
            console.log("Success:");
        })
        .catch(function (error) {
            console.error("Error:", error);
        });
    await showProgressBar();
    getPolygons();
}

//Функция для редаактирования полигонов

function enableEdit(layer) {
    calcNdvi(layer, true);
    layer.enableEdit(); //включаем редактирование для элемента
    layer.closePopup(); // закрываемвсплывающее окно
    //проводим манипуляции с кнопками в првой части экрана
    toggleButtonDisplay(false, true, true);

    //назначаем кнопкам функции
    document.getElementById("finishButton").onclick = function () {
        finishEdit(layer);
    };
    document.getElementById("cancelButton").onclick = function () {
        cancelEdit(layer);
        getPolygons();
    };

    //функция для применения изменений
    function finishEdit(layer) {
        document.removeEventListener("keydown", kedown);
        //выключаем редактирование
        layer.disableEdit();
        //фиксируем изменения как новый полигон и удаляем старый
        geojson = layer.toGeoJSON();
        updatePolygon(geojson);
        toggleButtonDisplay(true, false, false);
    }
    document.addEventListener("keydown", kedown);

    function kedown(event) {
        if (event.key === "Enter") finishEdit(layer);
    }

    //функция  отмены изменений
    function cancelEdit(layer) {
        toggleButtonDisplay(true, false, false);
        layer.disableEdit();
    }
}
