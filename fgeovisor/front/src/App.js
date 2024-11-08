import React, { useEffect, useState } from 'react';
import Map from './components/Map';
import Sidebar from './components/Sidebar';
import Modal from './components/Modal';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';

function App() {
    // Состояния для хранения данных из метатегов
    const [csrfToken, setCsrfToken] = useState(null);
    const [authCheck, setAuthCheck] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [loginError, setLoginError] = useState(false);
    const [regError, setRegError] = useState(false);
    const [permitionAccess, setPermitionAccess] = useState(false);

    useEffect(() => {
        // Получаем метатеги из документа
        const csrfTokenMeta = document.querySelector('[name=csrfmiddlewaretoken]');
        const authCheckMeta = document.querySelector('[name=auth_check]');
        const isAdminMeta = document.querySelector('[name=is_staff]');
        const loginErrorMeta = document.querySelector('[name=login_error]');
        const regErrorMeta = document.querySelector('[name=create_error]');
        const permitionAccessMeta = document.querySelector('[name=permition_access]');

        // Проверяем наличие метатегов и устанавливаем значения в состояние
        if (csrfTokenMeta) setCsrfToken(csrfTokenMeta.content);
        if (authCheckMeta) setAuthCheck(authCheckMeta.content === "True");
        if (isAdminMeta) setIsAdmin(isAdminMeta.content === "True");
        if (loginErrorMeta) setLoginError(loginErrorMeta.content === "True");
        if (regErrorMeta) setRegError(regErrorMeta.content === "True");
        if (permitionAccessMeta) setPermitionAccess(permitionAccessMeta.content === "True");
    }, []);

    // Передаем пропсы в дочерние компоненты
    return (
        <div>
            <Sidebar authCheck={authCheck} isAdmin={isAdmin} />
            <Map />
            <Modal>
                <LoginForm
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
