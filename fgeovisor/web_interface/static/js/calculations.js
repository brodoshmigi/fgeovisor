 //Функция рассчёта NDVI

function calcNdvi(layer){
    latlngBounds = layer.getLatLngs();
    console.log(latlngBounds);
    const requestURL = '/get-img/' + layer.id;
    const response = fetch(requestURL,  {   
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Добавляем CSRF-токен
            },
        })
        .then(response => {
            return response.json()
        })
        .then(data => {
            const {id, url} = data
            L.imageOverlay(url, latlngBounds).addTo(map);
        })
        /* Боже сохрани Promise!!! Да спасет java script Иисус Христос */
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