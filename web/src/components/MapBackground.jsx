import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, ZoomControl } from "react-leaflet";
import styled from "styled-components";
import "leaflet/dist/leaflet.css";
import { districtsData } from "../data/federal_districts/districts";
import { skfoRegions } from "../data/SKFO/regions";
import { yufoRegions } from "../data/YUFO/regions";
import { Button } from "../styles";

// Создаем обертку для MapContainer
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

function MapBackground({ theme, isAuthenticated }) {
    const mapRef = useRef(null);
    const [activeDistrict, setActiveDistrict] = useState(null);
    const [zoomLevel, setZoomLevel] = useState("districts"); // districts, regions
    const [previousView, setPreviousView] = useState(null);

    // Преобразуем объект в массив
    const districts = Object.values(districtsData);

    // Получаем регионы в зависимости от федерального округа
    const getRegionsByDistrict = (districtName) => {
        if (districtName === "Южный федеральный округ") {
            return yufoRegions;
        } else if (districtName === "Северо-Кавказский федеральный округ") {
            return skfoRegions;
        }
        return null;
    };

    useEffect(() => {
        if (mapRef.current) {
            if (isAuthenticated) {
                const russiaCoords = [65, 105];
                const zoom = 4;
                mapRef.current.setView(russiaCoords, zoom);
            } else {
                const defaultCoords = [0, 0];
                const defaultZoom = 3;
                mapRef.current.setView(defaultCoords, defaultZoom);
            }
        }
    }, [isAuthenticated]);

    const getTileUrl = () => {
        if (
            theme?.bg === "#38393c" ||
            (theme?.bg === "auto" &&
                window.matchMedia("(prefers-color-scheme: dark)").matches)
        ) {
            return "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
        }
        return "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    };

    // Добавляем функцию для вычисления центра полигона
    const getPolygonCenter = (coordinates) => {
        let minLat = 90,
            maxLat = -90,
            minLng = 180,
            maxLng = -180;

        // Обрабатываем все части полигона
        coordinates.forEach((polygon) => {
            polygon.forEach(([lng, lat]) => {
                minLat = Math.min(minLat, lat);
                maxLat = Math.max(maxLat, lat);
                minLng = Math.min(minLng, lng);
                maxLng = Math.max(maxLng, lng);
            });
        });

        return [(minLat + maxLat) / 2, (minLng + maxLng) / 2];
    };

    // Обработчик кнопки "Назад"
    const handleBack = () => {
        if (zoomLevel === "regions") {
            // Возвращаемся к виду России
            mapRef.current.flyTo([65, 105], 4, {
                duration: 1,
            });
            setZoomLevel("districts");
            setActiveDistrict(null);
        }
    };

    const onEachDistrict = (feature, layer) => {
        const districtName = feature.properties["Federal District"];
        layer.bindTooltip(districtName, { sticky: true });

        layer.on({
            mouseover: (e) => {
                const layer = e.target;
                layer.setStyle({
                    fillOpacity: 0.7,
                });
            },
            mouseout: (e) => {
                const layer = e.target;
                layer.setStyle({
                    fillOpacity: 0.3,
                });
            },
            click: (e) => {
                const center = getPolygonCenter(
                    e.target.feature.geometry.coordinates
                );
                // Сохраняем текущий вид перед изменением
                setPreviousView({
                    center: mapRef.current.getCenter(),
                    zoom: mapRef.current.getZoom(),
                });
                setActiveDistrict(districtName);
                setZoomLevel("regions");
                mapRef.current.flyTo(center, 7, {
                    duration: 1,
                });
            },
        });
    };

    const onEachRegion = (feature, layer) => {
        const regionName = feature.properties.name;
        layer.bindTooltip(regionName, { sticky: true });

        layer.on({
            mouseover: (e) => {
                const layer = e.target;
                layer.setStyle({ fillOpacity: 0.7 });
            },
            mouseout: (e) => {
                const layer = e.target;
                layer.setStyle({ fillOpacity: 0.3 });
            },
            click: (e) => {
                const center = getPolygonCenter(
                    e.target.feature.geometry.coordinates
                );
                mapRef.current.flyTo(center, 12, {
                    duration: 1,
                });
            },
        });
    };

    return (
        <MapWrapper isAuthenticated={isAuthenticated}>
            {zoomLevel === "regions" && (
                <Button
                    onClick={handleBack}
                    style={{
                        position: "absolute",
                        top: "20px",
                        left: "20px",
                        zIndex: 9999,
                    }}
                >
                    ← Назад
                </Button>
            )}
            <MapContainer
                ref={mapRef}
                center={isAuthenticated ? [65, 105] : [0, 0]}
                zoom={isAuthenticated ? 4 : 3}
                attributionControl={false}
                zoomControl={false}
            >
                <TileLayer
                    url={getTileUrl()}
                    attribution="&copy; OpenStreetMap contributors, &copy; CartoDB"
                />

                {isAuthenticated &&
                    zoomLevel === "districts" &&
                    districts.map((district, index) => (
                        <GeoJSON
                            key={index}
                            data={district}
                            style={() => ({
                                fillColor: theme?.accent || "#38393c",
                                weight: 2,
                                opacity: 1,
                                color: theme?.accent || "#38393c",
                                fillOpacity: 0.3,
                                zoom: 8,
                            })}
                            onEachFeature={onEachDistrict}
                        />
                    ))}

                {isAuthenticated &&
                    zoomLevel === "regions" &&
                    activeDistrict &&
                    Object.values(
                        getRegionsByDistrict(activeDistrict) || {}
                    ).map((region, index) => (
                        <GeoJSON
                            key={`region-${index}`}
                            data={region}
                            style={() => ({
                                fillColor: theme?.accent || "#38393c",
                                weight: 2,
                                opacity: 1,
                                color: theme?.accent || "#38393c",
                                fillOpacity: 0.3,
                            })}
                            onEachFeature={onEachRegion}
                        />
                    ))}
            </MapContainer>
        </MapWrapper>
    );
}

export default MapBackground;
