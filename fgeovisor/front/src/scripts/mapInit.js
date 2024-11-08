import L from 'leaflet/dist/leaflet.js';
import 'leaflet/dist/leaflet.js'
import 'leaflet/dist/leaflet.css'
import { getPolygons } from './polygonManager';
import * as utils from './utils'
import { switchsidebarcontent } from './uiControls';

export function initMap(container) {
    if (window.map){
        return;
    }
    var southWest = L.latLng(-85.0511287798, -180),
        northEast = L.latLng(85.0511287798, 180);
    var bounds = L.latLngBounds(southWest, northEast);

    window.map = L.map(container, {
        editable: true,//Включаем пакет, позволяющий производить редактирование объектов leaflet
        attributionControl: false,//отключаем ссылку на нытьё хохла
        maxBounds: bounds,
        maxBoundsViscosity: 1.0,
        minZoom: 3,
        zoomControl: false
    }).setView([45.03, 41.96], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(window.map);


    //подгрузка полигонов из БД
    window.polygonLayerGroup  = L.layerGroup().addTo(window.map);
    getPolygons();
    utils.bindValidation();
}