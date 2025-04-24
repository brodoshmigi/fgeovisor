import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import L from 'leaflet';

const ControlButton = styled.button`
    position: absolute;
    z-index: 1000;
    background: ${props => props.theme.accent};
    color: ${props => props.theme.bg};
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin: 4px;

    &:hover {
        opacity: 0.9;
    }
`;

const CreateButton = styled(ControlButton)`
    top: 100px;
    right: 4px;
`;

const FinishButton = styled(ControlButton)`
    top: 140px;
    right: 4px;
`;

const CancelButton = styled(ControlButton)`
    top: 180px;
    right: 4px;
`;

function FieldManager({ map, selectedRegion, theme }) {
    const [isCreating, setIsCreating] = useState(false);
    const [fields, setFields] = useState([]);
    const [drawingField, setDrawingField] = useState(null);

    useEffect(() => {
        if (selectedRegion) {
            fetchFields();
        }
    }, [selectedRegion]);

    const fetchFields = async () => {
        try {
            const response = await fetch("/api/crud/polygon");
            const data = await response.json();
            setFields(data);
        } catch (error) {
            console.error("Error fetching fields:", error);
        }
    };

    const startCreating = () => {
        setIsCreating(true);
        map.getContainer().style.cursor = "crosshair";
        
        const savedColor = localStorage.getItem("selectedColor") || "#1A4F63";
        const newField = L.polygon([], {
            color: savedColor,
            dashArray: "10, 5"
        }).addTo(map);
        
        setDrawingField(newField);
    };

    const finishCreating = () => {
        if (drawingField) {
            const geojson = drawingField.toGeoJSON();
            saveField(geojson);
            drawingField.remove();
            setDrawingField(null);
        }
        setIsCreating(false);
        map.getContainer().style.cursor = "";
    };

    const cancelCreating = () => {
        if (drawingField) {
            drawingField.remove();
            setDrawingField(null);
        }
        setIsCreating(false);
        map.getContainer().style.cursor = "";
    };

    const saveField = async (geojson) => {
        try {
            const response = await fetch("/api/crud/polygon", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(geojson),
            });
            if (response.ok) {
                fetchFields();
            }
        } catch (error) {
            console.error("Error saving field:", error);
        }
    };

    return (
        <>
            {!isCreating ? (
                <CreateButton onClick={startCreating}>
                    Создать поле
                </CreateButton>
            ) : (
                <>
                    <FinishButton onClick={finishCreating}>
                        Завершить
                    </FinishButton>
                    <CancelButton onClick={cancelCreating}>
                        Отменить
                    </CancelButton>
                </>
            )}
        </>
    );
}

export default FieldManager;