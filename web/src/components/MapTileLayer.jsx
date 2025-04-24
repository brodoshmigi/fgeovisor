import React from 'react';
import { TileLayer } from 'react-leaflet';

const MapTileLayer = ({ theme }) => {
    const getTileUrl = () => {
        if (
            theme?.bg === "#38393c" ||
            (theme?.bg === "auto" &&
                window.matchMedia("(prefers-color-scheme: dark)").matches)
        ) {
            return "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
        }
        return "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
    };

    return (
        <TileLayer
            url={getTileUrl()}
            attribution="&copy; OpenStreetMap contributors, &copy; CartoDB"
        />
    );
};

export default MapTileLayer;