// src/components/Modal.js
import React from 'react';
import { closeModal } from '../scripts/uiControls.js';

function Modal({ children }) {
    return (
        <div id="modal" className="modal" onClick={() => closeModal()}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="close" onClick={() => closeModal()}>&times;</span>
                <div className="modalBody" id="modalBody">
                    {children}
                </div>
            </div>
        </div>
    );
}

export default Modal;
