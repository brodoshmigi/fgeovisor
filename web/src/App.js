// File: src/App.jsx
import React, { useState, useEffect } from "react";
import { ThemeProvider } from "styled-components";
import MapBackground from "./components/MapBackground";
import InteractiveMap from "./components/InteractiveMap";
import LoginPage from "./components/LoginPage";
import RegistrationPage from "./components/RegistrationPage";
import SettingsMenu from "./components/SettingsMenu";
import SidePanel from "./components/SidePanel";
import { initializeCsrf } from "./utils/auth";
import { GlobalStyles } from "./styles";
import { getCsrfToken } from "./utils/auth";

function App() {
    const [theme, setTheme] = useState({ bg: "#38393c", accent: "#00a4cc" });
    const [currentPage, setCurrentPage] = useState("login");
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const isAuth = await initializeCsrf();
                if (isAuth && window.authcheck === "True") {
                    setIsAuthenticated(true);
                } else {
                    // Если авторизация не удалась - показываем окно входа
                    setIsAuthenticated(false);
                    setCurrentPage("login");
                }
            } catch (error) {
                console.error("Ошибка при проверке авторизации:", error);
                setIsAuthenticated(false);
                setCurrentPage("login");
            }
        };
        checkAuth();
    }, []);

    const navigateToRegister = () => setCurrentPage("register");
    const navigateToLogin = () => setCurrentPage("login");

    const handleLogin = () => {
        setIsAuthenticated(true);
    };

    const handleLogout = async () => {
        try {
            const response = await fetch("api/auth/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken("csrftoken"),
                },
                credentials: "include",
            });

            if (response.ok) {
                window.authcheck = "False";
                window.isadmin = "False";
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error("Ошибка при выходе:", error);
        }
    };

    const handleChangePassword = () => {
        // Здесь можно добавить логику открытия модального окна
        // для смены пароля или переход на отдельную страницу
        console.log("Смена пароля");
    };

    return (
        <>
            <GlobalStyles />
            <div style={{ backgroundColor: "transparent", height: "100vh" }}>
                <MapBackground theme={theme} isAuthenticated={isAuthenticated} />
                {isAuthenticated && (
                    <InteractiveMap theme={theme} isAuthenticated={isAuthenticated} />
                )}
                <ThemeProvider theme={theme}>
                    {isAuthenticated && (
                        <SidePanel
                            username="Username" // Замените на реальное имя пользователя
                            onLogout={handleLogout}
                            onChangePassword={handleChangePassword}
                        />
                    )}
                    <SettingsMenu setTheme={setTheme} />
                    {!isAuthenticated && (
                        <>
                            {currentPage === "login" && (
                                <LoginPage
                                    navigateToRegister={navigateToRegister}
                                    onLogin={handleLogin}
                                />
                            )}
                            {currentPage === "register" && (
                                <RegistrationPage
                                    navigateToLogin={navigateToLogin}
                                />
                            )}
                        </>
                    )}
                </ThemeProvider>
            </div>
        </>
    );
}

export default App;
