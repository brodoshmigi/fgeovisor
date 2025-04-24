// File: src/components/RegistrationPage.jsx
import React, { useState } from "react";
import styled from "styled-components";
import { getCsrfToken } from "../utils/auth";
import { Wrapper, Box, BaseButton } from "../styles";

const StyledForm = styled.form`
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    max-width: 300px;
    margin-bottom: 20px;
`;

const InputGroup = styled.div`
    display: flex;
    flex-direction: column;
    gap: 8px;

    label {
        font-size: 14px;
    }

    input {
        padding: 8px;
        border: 1px solid ${(props) => props.theme.accent};
        border-radius: 4px;
        background: transparent;
        color: ${(props) => props.theme.accent};

        &:focus {
            outline: none;
            box-shadow: 0 0 0 2px ${(props) => props.theme.accent}40;
        }
    }
`;

const Title = styled.h2`
    margin-bottom: 24px;
`;

const ErrorMessage = styled.div`
    color: #ff0000;
    font-size: 14px;
    margin-top: 10px;
`;

function RegistrationPage({ navigateToLogin, onLogin }) {
    const [error, setError] = useState("");
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        password2: ""
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (formData.password !== formData.password2) {
            setError("Пароли не совпадают");
            return;
        }

        try {
            const csrfToken = getCsrfToken("csrftoken");
            const response = await fetch("/api/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password
                }),
            });

            const result = await response.json();

            if (response.ok) {
                // После успешной регистрации сервер возвращает те же данные что и при авторизации
                window.authcheck = "True";
                window.isadmin = result.is_staff ? "True" : "False";
                onLogin();
            } else {
                setError(result.error || "Ошибка при регистрации");
            }
        } catch (error) {
            console.error("Error:", error);
            setError("Произошла ошибка при регистрации");
        }
    };

    return (
        <Wrapper>
            <Box>
                <Title>Регистрация</Title>
                <StyledForm onSubmit={handleSubmit}>
                    <InputGroup>
                        <label>Email:</label>
                        <input 
                            type="email" 
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required 
                        />
                    </InputGroup>
                    <InputGroup>
                        <label>Пароль:</label>
                        <input 
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required 
                        />
                    </InputGroup>
                    <InputGroup>
                        <label>Подтвердите пароль:</label>
                        <input 
                            type="password"
                            name="password2"
                            value={formData.password2}
                            onChange={handleChange}
                            required 
                        />
                    </InputGroup>
                    {error && <ErrorMessage>{error}</ErrorMessage>}
                    <BaseButton type="submit">Зарегистрироваться</BaseButton>
                </StyledForm>
                <BaseButton onClick={navigateToLogin}>
                    Уже есть аккаунт?
                </BaseButton>
            </Box>
        </Wrapper>
    );
}

export default RegistrationPage;
