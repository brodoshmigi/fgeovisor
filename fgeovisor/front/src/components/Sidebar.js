import React, { useEffect, useState, useRef, useImperativeHandle, forwardRef } from 'react';
import '../styles/styles.css'; // Импортируем стили
import Modal from './Modal'; // Импортируем компонент Modal
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm'

const Sidebar = forwardRef((props,ref) => {
    const [sidebarWidth, setSidebarWidth] = useState("0");
    const [isModalOpen, setisModalOpen] = useState(false);
    const [modalContent, setIsModalContent] = useState(null);
    const sidebarRef = useRef(null);
    const menuButtonRef = useRef(null);

    const toggleSidebar = () => {
        setSidebarWidth(sidebarWidth === "250px" ? "0px" : "250px");
    };

    const openModal = (content) => {
        setIsModalContent(content);
        setisModalOpen(true);
    };

    const closeModal = () => {
        setisModalOpen(false);
        setIsModalContent(null);
    };

    useImperativeHandle(ref,()=>({
        openModal
    }));

    const switchSidebarContent = () => {
        return (
            <div id="defoltview">
                <a href="#" onClick={() => openModal(<LoginForm />)}>Войти</a>
                <a href="#" onClick={() => openModal(<RegistrationForm />)}>Зарегистрироваться</a>
            </div>
        );
    };

    const handleClickOutside = (event) => {
        if (
            sidebarRef.current && !sidebarRef.current.contains(event.target) &&
            menuButtonRef.current && !menuButtonRef.current.contains(event.target)
        ) {
            setSidebarWidth("0px");
        }
    };

    useEffect(() => {
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div>
            <button
                id="menuButton"
                className="menu-button"
                ref={menuButtonRef}
                onClick={toggleSidebar}
            >
                ☰
            </button>

            <div
                id="sidebar"
                className="sidebar"
                style={{ width: sidebarWidth }}
                ref={sidebarRef}
            >
                {switchSidebarContent()}
            </div>
            <Modal isOpen={isModalOpen} onClose={closeModal}>
                {modalContent}
            </Modal>
        </div>
    );
});

export default Sidebar;

