import React from 'react';
import { GeoJSON } from 'react-leaflet';

function FieldsLayer({ fields, theme }) {
    const style = {
        color: localStorage.getItem("selectedColor") || "#1A4F63",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.3
    };

    const onEachField = (feature, layer) => {
        if (feature.properties) {
            const area = calculatePolygonArea(layer.getLatLngs()[0]);
            layer.bindPopup(`Площадь: ${area.toFixed(2)} га`);
        }
    };

    return (
        <GeoJSON 
            data={fields}
            style={style}
            onEachFeature={onEachField}
        />
    );
}

export default FieldsLayer;