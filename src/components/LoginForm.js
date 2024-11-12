// src/components/LoginForm.js
import React, { useRef } from 'react';
import '../styles/styles.css'
import Sidebar from './Sidebar';
import RegistrationForm from './RegistrationForm';

export const LoginForm = (sidebarRef) => {
    const openModalInSidebar = () => {
        if(sidebarRef.current){
            sidebarRef.current.openModal(<RegistrationForm />)
        }else{
            console.error('no sidebar ref')
        }
    }
    return (
        <div id="loginForm">
            <div className="errormsg" id="errormsg"><p>Неправильное имя пользователя или пароль</p></div>
            <h2>Вход</h2>
            <form method="post" action="/login">
                <input placeholder="Введите login" type="text" id="username" name="username" required />
                <input placeholder="Введите пароль" type="password" id="password" name="password" required />
                <button type="submit">Войти</button>
                <div className="login-help">
                    <a href='#' onClick={openModalInSidebar}>Нет аккаунта</a>
                </div>
            </form>
        </div>
    );
}

export default LoginForm;
