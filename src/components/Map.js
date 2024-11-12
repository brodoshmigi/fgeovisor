// src/components/Map.js
import React, { useEffect, useRef } from 'react';
import { initMap } from '../scripts/mapInit';

function Map() {
    const mapContainer = useRef(null);
    useEffect(() => {
        if(mapContainer.current){
            initMap(mapContainer.current);
        }
    }, []);
    return <div ref={mapContainer} style={{height:"100vh",width:"100%"}} />
}

export default Map;
