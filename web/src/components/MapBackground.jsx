import React from "react";
import { MapContainer } from "react-leaflet";
import styled from "styled-components";
import "leaflet/dist/leaflet.css";
import MapTileLayer from "./MapTileLayer";

const MapWrapper = styled.div`
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    z-index: 1;
    pointer-events: none;

    .leaflet-container {
        height: 100%;
        width: 100%;
    }
`;

function MapBackground({ theme }) {
    // Используем центральные координаты и меньший зум для общего вида
    const defaultCoords = [30, 0];

    return (
        <MapWrapper>
            <MapContainer
                center={defaultCoords}
                zoom="4"
                attributionControl={false}
                zoomControl={false}
                dragging={false}
                scrollWheelZoom={false}
            >
                <MapTileLayer theme={theme} />
            </MapContainer>
        </MapWrapper>
    );
}

export default MapBackground;
