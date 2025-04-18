// File: src/components/RegistrationPage.jsx
import React from "react";
import styled from "styled-components";
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

function RegistrationPage({ navigateToLogin }) {
    return (
        <Wrapper>
            <Box>
                <Title>Регистрация</Title>
                <StyledForm>
                    <InputGroup>
                        <label>Email:</label>
                        <input type="email" required />
                    </InputGroup>
                    <InputGroup>
                        <label>Пароль:</label>
                        <input type="password" required />
                    </InputGroup>
                    <InputGroup>
                        <label>Подтвердите пароль:</label>
                        <input type="password" required />
                    </InputGroup>
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
