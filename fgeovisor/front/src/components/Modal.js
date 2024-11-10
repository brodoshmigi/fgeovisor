// Modal.js
import React from 'react';
import '../styles/styles.css'

const Modal = ({ isOpen, onClose, children }) => {
    if (!isOpen) return null; // Если окно не открыто, ничего не рендерим

    return (
        <div className="modal-overlay">
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>X</button>
                {children}
            </div>
        </div>
    );
};

export default Modal;
