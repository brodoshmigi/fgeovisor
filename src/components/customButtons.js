// src/components/CustomButtons.js
import React, {useRef,useImperativeHandle, forwardRef } from 'react';
const buttonRefs = {
    create: React.createRef(),
    finish: React.createRef(),
    cancel: React.createRef(),
};

export const setCreateButtonHandler = (handler) => {
    if (buttonRefs.create.current){
        buttonRefs.create.current.onclick = handler;
    }
}
export const setFinishButtonHandler = (handler) => {
    if (buttonRefs.finish.current){
        buttonRefs.finish.current.onclick = handler;
    }
}
export const setCancelButtonHandler = (handler) => {
    if (buttonRefs.cancel.current){
        buttonRefs.cancel.current.onclick = handler;
    }
}

const CustomButtons = (_, ref) => {

    useImperativeHandle(ref, () => ({
        setCreateButtonHandler,
        setFinishButtonHandler,
        setCancelButtonHandler,
        }));

    return (
        <div className="ui-button" id="ui-button">
            <button
            id="createButton" 
            ref={buttonRefs.create} 
            style={{display: 'block'}}
            >
                Добавить поле
            </button>
            <button
                id="finishButton"
                ref={buttonRefs.finish}
                style={{ display: 'none' }}
            >
                Применить
            </button>
            <button
                id="cancelButton"
                ref={buttonRefs.cancel}
                style={{ display: 'none' }}
            >
                Отменить
            </button>
        </div>
    );
};

export default CustomButtons;
