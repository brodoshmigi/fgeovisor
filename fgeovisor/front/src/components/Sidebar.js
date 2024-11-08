// src/components/Sidebar.js
import React from 'react';
import {showLoginForm} from '../scripts/uiControls';
import {showRegistrationForm} from '../scripts/uiControls';

function Sidebar() {
    return (
        <div id="sidebar" className="sidebar" style={{ width: 0 }}>
            <div id="defoltview">
                <a href="#" onClick={showLoginForm}>Войти</a>
                <a href="#" onClick={showRegistrationForm}>Зарегистрироваться</a>
            </div>
            <div id="loggedinbuttons">
                <div id="superuser">
                    <a href="/admin">Панель админа</a>
                </div>
                <a href="/logout">Выйти</a>
            </div>
        </div>
    );
}

export default Sidebar;
