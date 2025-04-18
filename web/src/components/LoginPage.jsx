// File: src/components/LoginPage.jsx
import React, { useState } from "react";
import styled from "styled-components";
import { getCsrfToken } from "../utils/auth";
import { Wrapper, Box, Button } from "../styles";

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

function LoginPage({ navigateToRegister, onLogin }) {
    const [error, setError] = useState("");
    const [formData, setFormData] = useState({
        username: "",
        password: "",
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

        try {
            const csrfToken = getCsrfToken("csrftoken");
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (result.auth_check) {
                window.authcheck = "True";
                window.isadmin = result.is_staff ? "True" : "False";
                onLogin();
            } else {
                setError("Неверный логин или пароль");
            }
        } catch (error) {
            console.error("Error:", error);
            setError("Произошла ошибка при авторизации");
        }
    };

    return (
        <Wrapper>
            <Box>
                <Title>Авторизация</Title>
                <StyledForm onSubmit={handleSubmit}>
                    <InputGroup>
                        <label>Логин:</label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
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
                    {error && <ErrorMessage>{error}</ErrorMessage>}
                    <Button type="submit">Войти</Button>
                </StyledForm>
                <Button onClick={navigateToRegister}>Зарегистрироваться</Button>
            </Box>
        </Wrapper>
    );
}

export default LoginPage;
