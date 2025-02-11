import { autoSwitchTheme, switchsidebarcontent } from "./uiControls.js";

var map;
function initMap() {
    var southWest = L.latLng(-85.0511287798, -180),
        northEast = L.latLng(85.0511287798, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    map = L.map("map", {
        editable: true, //Включаем пакет, позволяющий производить редактирование объектов leaflet
        attributionControl: false, //отключаем ссылку на нытьё хохла
        maxBounds: bounds,
        maxBoundsViscosity: 1.0,
        minZoom: 3,
        zoomControl: false,
    }).setView([45.03, 41.96], 13);

    const attributionControl = L.control
        .attribution({
            prefix: "",
        })
        .addTo(map);

    L.tileLayer(
        "https://core-renderer-tiles.maps.yandex.net/tiles?l=map&x={x}&y={y}&z={z}",
        {
            attribution: "© Яндекс",
        }
    ).addTo(map);

    window.map = map;

    fetch("/static/geojson/Russia_regions.geojson")
        .then((response) => response.json())
        .then((data) => {
            L.geoJSON(data, {
                style: function (feature) {
                    return {
                        color: "#ff7800", // Цвет границы
                        weight: 2, // Толщина линии
                        opacity: 1, // Прозрачность линии
                        fillOpacity: 0, // Прозрачность заливки
                    };
                },
            }).addTo(map);
        });

    //подгрузка полигонов из БД
    polygonLayerGroup = L.layerGroup().addTo(map);
    if (authcheck === "True") {
        getPolygons();
    }
    bindValidation();
}

// Инициализация карты при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
    initMap();
    bindValidation();
    bulling();
    switchsidebarcontent();
    autoSwitchTheme();
});
