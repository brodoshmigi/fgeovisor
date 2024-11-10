// App.js
import React, { useEffect, useState, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Map from './components/Map';
import Modal from './components/Modal';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';
import './styles/styles.css';

function App() {
    const sidebarRef = useRef(null);
    const [csrfToken, setCsrfToken] = useState(null);
    const [authCheck, setAuthCheck] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [loginError, setLoginError] = useState(false);
    const [regError, setRegError] = useState(false);

    useEffect(() => {
        const csrfTokenMeta = document.querySelector('[name=csrfmiddlewaretoken]');
        const authCheckMeta = document.querySelector('[name=auth_check]');
        const isAdminMeta = document.querySelector('[name=is_staff]');
        const loginErrorMeta = document.querySelector('[name=login_error]');
        const regErrorMeta = document.querySelector('[name=create_error]');

        if (csrfTokenMeta) setCsrfToken(csrfTokenMeta.content);
        if (authCheckMeta) setAuthCheck(authCheckMeta.content === "True");
        if (isAdminMeta) setIsAdmin(isAdminMeta.content === "True");
        if (loginErrorMeta) setLoginError(loginErrorMeta.content === "True");
        if (regErrorMeta) setRegError(regErrorMeta.content === "True");
    }, []);

    // Передаем пропсы и реф в дочерние компоненты
    return (
        <div>
            <Sidebar ref={sidebarRef} authCheck={authCheck} isAdmin={isAdmin} />
            <Map />
            <Modal>
                <LoginForm 
                    sidebarRef={sidebarRef} 
                    loginError={loginError} 
                    setAuthCheck={setAuthCheck} 
                    setIsAdmin={setIsAdmin} 
                    setLoginError={setLoginError}
                />
                <RegistrationForm 
                    regError={regError} 
                    setRegError={setRegError} 
                />
            </Modal>
        </div>
    );
}

export default App;
