var map;
function initMap() {
    var southWest = L.latLng(-85.0511287798, -180),
        northEast = L.latLng(85.0511287798, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    map = L.map('map', {
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
    polygonLayerGroup  = L.layerGroup().addTo(map);
    if (authcheck === "True"){
        getPolygons();
    }
    bindValidation();
}

// Инициализация карты при загрузке страницы
document.addEventListener("DOMContentLoaded", function() {
    initMap();
    bindValidation();
    bulling();
    switchsidebarcontent();
});