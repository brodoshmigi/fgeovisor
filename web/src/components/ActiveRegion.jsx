import React from 'react';
import { GeoJSON } from 'react-leaflet';

function ActiveRegion({ region, theme }) {
    if (!region) return null;

    const activeStyle = {
        fillOpacity: 0,
        color: theme.accent,
        weight: 2,
        interactive: false // Отключаем интерактивность полигона
    };

    return (
        <GeoJSON 
            data={region} 
            style={activeStyle}
        />
    );
}

export default ActiveRegion;