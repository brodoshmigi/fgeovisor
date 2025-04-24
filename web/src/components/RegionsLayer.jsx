import React from 'react';
import { GeoJSON } from 'react-leaflet';

function RegionsLayer({ regions, theme, onRegionSelect }) {
    const regionStyle = {
        fillColor: theme.accent,
        fillOpacity: 0.4,
        color: theme.bg,
        weight: 1
    };

    return (
        <GeoJSON
            data={regions}
            style={regionStyle}
            onEachFeature={(feature, layer) => {
                layer.on({
                    click: () => onRegionSelect(feature)
                });
                layer.options.className = 'clickable-polygon';
            }}
        />
    );
}

export default RegionsLayer;