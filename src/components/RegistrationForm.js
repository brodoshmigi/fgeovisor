// src/components/RegistrationForm.js
import React from 'react';

function RegistrationForm() {
    return (
        <div id="registrationForm">
            <div className="errormsg" id="errorrg"><p>Неверные данные или пользователь уже существует</p></div>
            <h2>Регистрация</h2>
            <form method="post" action="/signup">
                <input placeholder="Введите имя пользователя" type="text" id="UserName" name="username" required />
                <input placeholder="Введите email" type="text" id="regEmail" name="email" required />
                <input placeholder="Введите пароль" type="password" id="regPassword" name="password" required />
                <input placeholder="Повторите пароль" type="password" id="passwordConfirmation" name="passwordConfirmation" required />
                <button type="submit">Зарегистрироваться</button>
            </form>
        </div>
    );
}

export default RegistrationForm;
