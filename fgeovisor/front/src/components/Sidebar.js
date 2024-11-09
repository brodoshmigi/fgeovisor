// Sidebar.js
import React, { useEffect, useState, useRef } from 'react';
import '../styles/styles.css'; // Импортируем стили
import Modal from './Modal'; // Импортируем компонент Modal
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm'

const Sidebar = () => {
    // Состояния для управления сайдбаром, модальными окнами и проверками авторизации
    const [sidebarWidth, setSidebarWidth] = useState("0");
    const [isModalOpen, setisModalOpen] = useState(false);
    const [modalContent, setIsModalContent] = useState(null);
    const sidebarRef = useRef(null);

    // Функция для переключения бокового меню (выезд/сворачивание)
    const toggleSidebar = () => {
        setSidebarWidth(sidebarWidth === "250px" ? "0px" : "250px");
    };

    // Функция для открытия модального окна
    const openModal = (content) => {
        console.log(content)
        setIsModalContent(content);
        setisModalOpen(true);
        console.log(isModalOpen)
    };

    // Функция для закрытия модального окна
    const closeModal = () => {
        setisModalOpen(false);
        setIsModalContent(null);
    };

    // Функция для обработки формы входа
    const handleLoginSubmit = (event) => {
        event.preventDefault();
        // Логика обработки входа, если ошибка - setLoginError(true)
    };

    // Функция для обработки формы регистрации
    const handleRegistrationSubmit = (event) => {
        event.preventDefault();
        // Логика обработки регистрации, если ошибка - setRegError(true)
    };

    // Функция для отображения содержимого бокового меню в зависимости от авторизации
    const switchSidebarContent = () => {
        return (
            <div id="defoltview">
                <a href="#" onClick={() => openModal(LoginForm)}>Войти</a>
                <a href="#" onClick={() => openModal(RegistrationForm)}>Зарегистрироваться</a>
            </div>
        );
    };

    const handleClickOutside = (event) => {
        if (!isModalOpen){
            setSidebarWidth("0px")
        }
    };

    useEffect(()=>{
        document.addEventListener("mousedown",handleClickOutside);
    }, [!isModalOpen]);

    return (
        <div>
            <button id="menuButton" className="menu-button" onClick={toggleSidebar}>☰</button>

            <div id="sidebar" className="sidebar" style={{ width: sidebarWidth }}>
                {switchSidebarContent()}
            </div>

            <Modal isOpen={isModalOpen} onClose={closeModal}>
                {modalContent === 'login' ? (
                    <LoginForm onSubmit={handleLoginSubmit} />
                ) : modalContent === 'register' ? (
                    <RegistrationForm onSubmit={handleRegistrationSubmit} />
                ) : null}
            </Modal>
        </div>
    );
};

export default Sidebar;
