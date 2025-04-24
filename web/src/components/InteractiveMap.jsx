import React, { useRef, useState } from "react";
import { MapContainer } from "react-leaflet";
import styled from "styled-components";
import "leaflet/dist/leaflet.css";
import { stavropol } from "../data/Stavropol.js";
import MapTileLayer from "./MapTileLayer";
import RegionsLayer from "./RegionsLayer";
import ActiveRegion from "./ActiveRegion";
import FieldManager from "./FieldManager";
import FieldsLayer from "./FieldsLayer";
import Button from './common/Button';

const MapWrapper = styled.div`
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    z-index: 2;
    pointer-events: ${(props) => (props.selectedRegion ? "auto" : "none")};

    .leaflet-container {
        height: 100%;
        width: 100%;
        background-color: ${({ theme }) => theme.mapBackground};
    }

    .clickable-polygon {
        pointer-events: bounding-box !important;
        cursor: pointer !important;
        touch-action: none;
    }

    .leaflet-tile {
        filter: ${({ theme }) => theme.mapFilter};
    }

    .leaflet-interactive {
        pointer-events: none;
    }

    .leaflet-interactive.clickable-polygon {
        touch-action: none;
        -ms-touch-action: none;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
`;

function InteractiveMap({ theme, isAuthenticated }) {
    const [selectedFeature, setSelectedFeature] = useState(null);
    const [maxBounds, setMaxBounds] = useState(null);
    const [fields, setFields] = useState([]);
    const mapRef = useRef();

    const russiaCoords = [65, 95];
    const russiaZoom = 4;

    const handleRegionSelect = (feature) => {
        setSelectedFeature(feature);
        // Устанавливаем границы на основе выбранного полигона
        const bounds = new L.GeoJSON(feature).getBounds();
        setMaxBounds(bounds);

        // Включаем взаимодействие с картой
        const map = mapRef.current;

        // Приближаем карту к выбранному региону
        map.fitBounds(bounds, {
            padding: [50, 50], // Отступ от краев
            maxZoom: 12, // Максимальное приближение
            animate: true, // Плавная анимация
        });

        map.dragging.enable();
        map.scrollWheelZoom.enable();
        map.doubleClickZoom.enable();

        // Устанавливаем ограничения
        map.setMaxBounds(bounds);
        map.setMinZoom(map.getZoom());
    };

    const handleRegionDeselect = () => {
        setSelectedFeature(null);
        setMaxBounds(null);
        // Возвращаем карту в исходное положение
        const map = mapRef.current;
        map.setMaxBounds(null);
        map.setView(russiaCoords, russiaZoom);
        // Отключаем взаимодействие с картой
        map.dragging.disable();
        map.scrollWheelZoom.disable();
        map.doubleClickZoom.disable();
    };

    return (
        <MapWrapper selectedRegion={selectedFeature} theme={theme}>
            {selectedFeature && (
                <>
                    <Button 
                        onClick={handleRegionDeselect}
                        $small
                        $position={{ top: 60, right: 4 }}
                    >
                        Выбрать другой регион
                    </Button>
                    {isAuthenticated && (
                        <FieldManager 
                            map={mapRef.current}
                            selectedRegion={selectedFeature}
                            theme={theme}
                        />
                    )}
                </>
            )}

            <MapContainer
                ref={mapRef}
                center={russiaCoords}
                zoom={russiaZoom}
                dragging={false}
                scrollWheelZoom={false}
                doubleClickZoom={false}
                attributionControl={false}
                zoomControl={false}
                maxBounds={maxBounds}
                maxBoundsViscosity={1.0}
                style={{ height: "100%", width: "100%" }}
            >
                <MapTileLayer theme={theme} />

                {!selectedFeature && (
                    <RegionsLayer
                        regions={stavropol}
                        theme={theme}
                        onRegionSelect={handleRegionSelect}
                    />
                )}

                {selectedFeature && (
                    <>
                        <ActiveRegion region={selectedFeature} theme={theme} />
                        <FieldsLayer fields={fields} theme={theme} />
                    </>
                )}
            </MapContainer>
        </MapWrapper>
    );
}

export default InteractiveMap;
