import React, { useState } from "react";
import styled from "styled-components";

const Panel = styled.div`
    position: fixed;
    left: ${(props) => (props.$isOpen ? "0" : "-320px")}; // Увеличили отступ
    top: 0;
    width: 300px;
    height: 100%;
    background-color: ${(props) => props.theme.bg};
    color: ${(props) => props.theme.accent};
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
    transition: left 0.3s ease;
    z-index: 1000;
    padding: 20px;
    visibility: ${(props) => (props.$isOpen ? "visible" : "hidden")};
`;

const ToggleButton = styled.button`
    position: fixed;
    left: 10px; // Фиксированное положение
    top: 10px;
    background-color: ${(props) => props.theme.accent};
    color: ${(props) => props.theme.bg};
    border: none;
    border-radius: 4px;
    padding: 8px;
    cursor: pointer;
    z-index: 1001;

    &:hover {
        opacity: 0.9;
    }
`;

const UserInfo = styled.div`
    margin-top: 60px;
    padding: 20px 0;
    border-bottom: 1px solid ${(props) => props.theme.accent}40;
`;

const Button = styled.button`
    width: 100%;
    padding: 10px;
    margin: 10px 0;
    background-color: ${(props) => props.theme.accent};
    color: ${(props) => props.theme.bg};
    border: none;
    border-radius: 4px;
    cursor: pointer;

    &:hover {
        opacity: 0.9;
    }
`;

function SidePanel({ login, onLogout, onChangePassword }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            <ToggleButton onClick={() => setIsOpen(!isOpen)}>
                {isOpen ? "✕" : "☰"}
            </ToggleButton>

            <Panel $isOpen={isOpen}>
                <UserInfo>
                    <h3>Профиль</h3>
                    <p>Пользователь: {login}</p>
                    {window.isadmin === "True" && <p>Статус: Администратор</p>}
                </UserInfo>

                <Button onClick={onChangePassword}>Сменить пароль</Button>

                <Button onClick={onLogout}>Выйти</Button>
            </Panel>
        </>
    );
}

export default SidePanel;
