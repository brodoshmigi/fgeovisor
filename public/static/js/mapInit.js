var authcheck, isadmin, loginerror, regerror, permition_access;
var map;
var csrfToken
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
document.addEventListener("DOMContentLoaded",async function() {
    fetch ('http://127.0.0.1:8001/api/')
            .then(response => response.json())
            .then(data =>{
                console.log(data)
                authcheck = data.auth_check ? "True" : "False";
                isadmin = data.is_staff ? "True" : "False";
                loginerror = data.login_error ? "True" : "False";
                regerror = data.is_valid_error ? "True" : "False";
                permition_access = data.create_error ? "True" : "False";
                csrfToken = document.cookie.split(';').find(row => row.startsWith('csrftoken='));
                csrfToken = csrfToken.replace("csrftoken=","");
            })
            .catch(error =>{
                console.error(error);
            })
    await delay(200);
    initMap();
    bindValidation();
    bulling();
    console.log(authcheck);
    console.log(csrfToken);
    switchsidebarcontent();
});