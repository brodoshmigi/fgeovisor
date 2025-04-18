export const initializeCsrf = async () => {
    try {
        const response = await fetch("api/csrf", {
            credentials: "include",
        });

        if (!response.ok) {
            return false;
        }

        const data = await response.json();

        // Проверяем что auth_check явно true
        if (data && data.auth_check === true) {
            window.authcheck = "True";
            window.isadmin = data.is_staff ? "True" : "False";
            return true;
        }

        // Если auth_check не true - сбрасываем флаги и возвращаем false
        window.authcheck = "False";
        window.isadmin = "False";
        return false;
    } catch (error) {
        console.error("Ошибка при получении CSRF токена:", error);
        // При ошибке сбрасываем флаги
        window.authcheck = "False";
        window.isadmin = "False";
        return false;
    }
};

export const getCsrfToken = (name) => {
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
    }
    return null;
};
