var savedTheme = localStorage.getItem("theme");

export function toggleButtonDisplay(
    createVisible,
    finishVisible,
    cancelVisible
) {
    const createButton = document.getElementById("createButton");
    const finishButton = document.getElementById("finishButton");
    const cancelButton = document.getElementById("cancelButton");

    if (createButton)
        createButton.style.display = createVisible ? "block" : "none";
    if (finishButton)
        finishButton.style.display = finishVisible ? "block" : "none";
    if (cancelButton)
        cancelButton.style.display = cancelVisible ? "block" : "none";
}

window.toggleButtonDisplay = toggleButtonDisplay;

// Функция для переключения бокового меню
export function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menuButton");

    if (sidebar && menuButton) {
        sidebar.style.width = sidebar.style.width === "250px" ? "0" : "250px";
        if (savedTheme) {
            if (savedTheme === "light") {
                menuButton.style.border =
                    sidebar.style.width === "250px"
                        ? "0px solid #20bab0"
                        : "1px solid #20bab0";
            } else {
                menuButton.style.border = "0px solid #20bab0";
                menuButton.style.boxShadow =
                    sidebar.style.width === "250px"
                        ? "none"
                        : "0 2px 5px rgba(0, 0, 0, 0.3)";
            }
        }
    }
}

window.toggleSidebar = toggleSidebar;

// Функция для открытия модального окна
function openModal() {
    const modal = document.getElementById("modal");
    if (modal) {
        modal.style.display = "block";
        modal.addEventListener("click", handleOutsideClick);
    }
}

// Функция для закрытия модального окна
export function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) {
        modal.style.display = "none";
        const modalBody = document.getElementById("modalBody");
        if (modalBody) modalBody.innerHTML = "";
        loginerror = "False";
        regerror = "False";
        modal.removeEventListener("click", handleOutsideClick);
    }
}

window.closeModal = closeModal;

function handleOutsideClick(event) {
    const modalContent = document.getElementById("modal-content");
    if (modalContent && !modalContent.contains(event.target)) {
        closeModal();
    }
}

// Функция для отображения формы входа
export function showLoginForm() {
    const modalBody = document.getElementById("modalBody");
    const modal = document.getElementById("modal-content");

    if (modalBody && modal) {
        modalBody.innerHTML = document.getElementById("loginForm").innerHTML;
        modal.style.width = "35%";
        modal.style.height = "350px";
        openModal();

        const passwordFields = document.querySelectorAll(
            "#modalBody input[type='password']"
        );
        passwordFields.forEach(function (field) {
            field.style.width = "100%";
        });
    }
}

window.showLoginForm = showLoginForm;

// Функция для отображения формы регистрации
export function showRegistrationForm() {
    const modalBody = document.getElementById("modalBody");
    const modal = document.getElementById("modal-content");

    if (modalBody && modal) {
        modalBody.innerHTML =
            document.getElementById("registrationForm").innerHTML;
        modal.style.width = "36%";
        modal.style.height = "350px";
        if (regerror === "True") {
            const errorRg = document.getElementById("errorrg");
            if (errorRg) errorRg.style.display = "block";
        }
        openModal();

        const form = document.querySelector("form[action]");
        if (form) {
            form.addEventListener("submit", function (event) {
                const password = document.getElementById("regPassword").value;
                const confirmPassword = document.getElementById(
                    "passwordConfirmation"
                ).value;
                if (password !== confirmPassword) {
                    alert("Пароли не совпадают!");
                    event.preventDefault();
                }
            });
        }
    }
}

window.showRegistrationForm = showRegistrationForm;

// Смена бокового меню для пользователя
export function switchsidebarcontent() {
    const createButton = document.getElementById("createButton");
    const loggedInButtons = document.getElementById("loggedinbuttons");
    const defoltView = document.getElementById("defoltview");
    const superuser = document.getElementById("superuser");
    const uiButton = document.getElementById("ui-button");

    if (authcheck === "False") {
        if (createButton) createButton.style.display = "none";
        if (loggedInButtons) loggedInButtons.style.display = "none";
        if (defoltView) defoltView.style.display = "block";
    } else {
        if (loggedInButtons) loggedInButtons.style.display = "block";
        if (defoltView) defoltView.style.display = "none";
        if (isadmin === "False") {
            if (superuser) superuser.style.display = "none";
        } else {
            if (superuser) superuser.style.display = "block";
        }
        if (uiButton) uiButton.style.display = "block";
    }

    if (loginerror === "True") {
        showLoginForm();
    }
    if (regerror === "True") {
        showRegistrationForm();
    }
}

window.switchsidebarcontent = switchsidebarcontent;

// Функции для работы с темами
export function switchTheme(themChoose) {
    const themeLink = document.getElementById("theme");
    if (themeLink) {
        if (themChoose === "dark") {
            themeLink.setAttribute("href", staticUrls.dark);
            localStorage.setItem("theme", "dark");
            savedTheme = "dark";
        } else {
            themeLink.setAttribute("href", staticUrls.light);
            localStorage.setItem("theme", "light");
            savedTheme = "light";
        }
    }
}

window.switchTheme = switchTheme;

export function autoSwitchTheme() {
    const themeLink = document.getElementById("theme");
    const savedTheme = localStorage.getItem("theme");
    const savedColor = localStorage.getItem("selectedColor");

    if (themeLink) {
        if (savedTheme) {
            if (savedTheme === "dark") {
                themeLink.setAttribute("href", staticUrls.dark);
            } else {
                themeLink.setAttribute("href", staticUrls.light);
            }
        } else {
            if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
                themeLink.setAttribute("href", staticUrls.dark);
            } else {
                themeLink.setAttribute("href", staticUrls.light);
            }
        }
    }

    if (savedColor) {
        polygonLayerGroup.eachLayer(function (layer) {
            layer.setStyle({ color: savedColor });
        });

        const colorLink = document.getElementById("colors");
        if (colorLink) {
            colorLink.setAttribute("href", staticUrls[savedColor]);
        }
    }
}

window.autoSwitchTheme = autoSwitchTheme;

export function switchColor(color) {
    const colorLink = document.getElementById("colors");
    let selectedColor;

    if (color === "blue_crayola") {
        selectedColor = "#1A4F63";
    } else if (color === "dark_cyan") {
        selectedColor = "#068587";
    } else if (color === "green_crayola") {
        selectedColor = "#6FB07F";
    } else if (color === "orange_crayola") {
        selectedColor = "#FCB03C";
    }

    if (colorLink) {
        colorLink.setAttribute("href", staticUrls[selectedColor]);
    }

    polygonLayerGroup.eachLayer(function (layer) {
        layer.setStyle({ color: selectedColor });
    });

    localStorage.setItem("selectedColor", selectedColor);
}

window.switchColor = switchColor;

export function showThemeSettings() {
    const modalBody = document.getElementById("modalBody");
    const modal = document.getElementById("modal-content");

    if (modalBody && modal) {
        modalBody.innerHTML =
            document.getElementById("themeSettings").innerHTML;
        modal.style.width = "350px";
        modal.style.height = "auto";
        openModal();
    }
}

window.showThemeSettings = showThemeSettings;

// Функция для получения событий из календаря
async function fetchPublicCalendarEvents() {
    const url = '/get-events/'

    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.items;
    } catch (error) {
        console.error("Ошибка при получении событий:", error);
        return [];
    }
}

// Функция для отображения событий на странице
export function displayEvents(events) {
    const eventsContainer = document.getElementById("events-container");
    if (!eventsContainer) {
        console.error("Контейнер для событий не найден!");
        return;
    }

    // Очищаем контейнер перед добавлением новых событий
    eventsContainer.innerHTML = "";

    if (events.length === 0) {
        eventsContainer.innerHTML = "<p>Событий нет.</p>";
        return;
    }

    return new Promise((resolve) => {
        events.forEach((event) => {
            const eventElement = document.createElement("button");
            eventElement.className = "event-button";
            eventElement.innerHTML = `
            <p>${new Date(event.start.date).toLocaleDateString()}</p>
            `;
            eventElement.addEventListener("click", function () {
                calendarWrapper.style.display = "none";
                resolve(event.start.date);
            });
            eventsContainer.appendChild(eventElement);
        });
    });
}

// Функция для отображения календаря
export async function handleCalendarClick() {
    const calendarWrapper = document.getElementById("calendarWrapper");
    if (calendarWrapper) {
        calendarWrapper.style.display = "block";
        const events = await fetchPublicCalendarEvents();
        const selectedDate = await displayEvents(events);
        return selectedDate;
    }
}

window.handleCalendarClick = handleCalendarClick;
