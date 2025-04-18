import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { BaseButton } from "../styles";

const MenuWrapper = styled.div`
    position: fixed; // Меняем на fixed
    top: 50px;
    right: 10px;
    background-color: ${(props) => props.theme.bg};
    color: ${(props) => props.theme.accent};
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    display: ${(props) => (props.$isVisible ? "block" : "none")};
    z-index: 1000; // Увеличиваем z-index
`;

const MenuContainer = styled.div`
    position: fixed; // Меняем на fixed
    top: 0;
    right: 0;
    width: auto;
    height: auto;
    z-index: 1000;
`;

const ToggleButton = styled(BaseButton)`
    position: fixed; // Меняем на fixed
    top: 10px;
    right: 10px;
    z-index: 1000;
`;

const StyledButton = styled(BaseButton)`
    background-color: ${(props) =>
        props.$isAccentButton ? props.$accentColor : props.theme.accent};
`;

function SettingsMenu({ setTheme }) {
    const [isVisible, setIsVisible] = useState(false);

    const themes = {
        dark: { bg: "#38393c", accent: "#00a4cc" },
        light: { bg: "#ffffff", accent: "#00a4cc" },
        browser: { bg: "auto", accent: "auto" },
    };

    // Добавляем определение системной темы
    const getSystemTheme = () => {
        if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            return themes.dark;
        }
        return themes.light;
    };

    // Слушаем изменения системной темы
    useEffect(() => {
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

        const handleChange = () => {
            if (themes.bg === "auto") {
                setTheme(getSystemTheme());
            }
        };

        mediaQuery.addListener(handleChange);
        return () => mediaQuery.removeListener(handleChange);
    }, [setTheme]);

    // Обновляем обработчик клика для кнопки выбора темы
    const handleThemeChange = (themeName) => {
        if (themeName === "browser") {
            setTheme(getSystemTheme());
        } else {
            setTheme(themes[themeName]);
        }
    };

    const accentColors = {
        blue: "#00a4cc",
        orange: "#ffa500",
        cyan: "#008b8b",
        green: "#32cd32",
    };

    const handleAccentChange = (colorName) => {
        setTheme((prevTheme) => ({
            ...prevTheme,
            accent: accentColors[colorName],
        }));
    };

    return (
        <MenuContainer>
            <ToggleButton onClick={() => setIsVisible(!isVisible)}>
                {isVisible ? "Закрыть" : "Открыть настройки"}
            </ToggleButton>
            <MenuWrapper $isVisible={isVisible}>
                <h3>Настройки темы</h3>
                <div>
                    <h4>База:</h4>
                    {Object.keys(themes).map((themeName) => (
                        <StyledButton
                            small
                            key={themeName}
                            onClick={() => handleThemeChange(themeName)}
                        >
                            {themeName}
                        </StyledButton>
                    ))}
                </div>
                <div>
                    <h4>Акцент:</h4>
                    {Object.keys(accentColors).map((colorName) => (
                        <StyledButton
                            small
                            key={colorName}
                            onClick={() => handleAccentChange(colorName)}
                            $isAccentButton
                            $accentColor={accentColors[colorName]}
                        >
                            {colorName}
                        </StyledButton>
                    ))}
                </div>
            </MenuWrapper>
        </MenuContainer>
    );
}
export default SettingsMenu;
