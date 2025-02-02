async function auth(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const data = { username: username, password: password };
  try {
    const response = await fetch("log-in/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();

    window.authcheck = result.auth_check ? "True" : "False";
    window.isadmin = result.is_staff ? "True" : "False";

    if (result.auth_check) {
      switchsidebarcontent();
      autoSwitchTheme();
      initGoogleAPI();
      closeModal();
      toggleButtonDisplay(true, false, false);
      getCookie("csrftoken");
      if (window.map) {
        await getPolygons();
      }
    } else {
      document.getElementById("errormsg").style.display = "block";
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function register(event) {
  event.preventDefault();
  const username = document.getElementById("UserName").value;
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;
  const passwordConfirmation = document.getElementById(
    "passwordConfirmation"
  ).value;

  if (password !== passwordConfirmation) {
    document.getElementById("errorrg").innerHTML = "Пароли не совпадают";
    document.getElementById("errorrg").style.display = "block";
    alert("НЕ РАБОТАЕТ");
    return;
  }

  const data = { username: username, email: email, password: password };
  try {
    const response = await fetch("sign-in/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    });
    const result = await response.json();
    window.authcheck = result.auth_check ? "True" : "False";
    window.isadmin = result.is_staff ? "True" : "False";

    if (result.auth_check) {
      switchsidebarcontent();
      autoSwitchTheme();
      initGoogleAPI();
      closeModal();
      toggleButtonDisplay(true, false, false);
      getCookie("csrftoken");
    } else {
      document.getElementById("errorrg").innerHTML =
        "Неверные данные или пользователь уже существует";
      document.getElementById("errorrg").style.display = "block";
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function logout() {
  try {
    const response = await fetch("log-out/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });
    if (response.ok) {
      window.authcheck = "False";
      window.isadmin = "False";
      switchsidebarcontent();
      initGoogleAPI();
      toggleButtonDisplay(false, false, false);
      getCookie("csrftoken");
      polygonLayerGroup.eachLayer((layer) => {
        Object.values(layer._layers).forEach((subLayer) => {
          calcNdvi(subLayer.feature, true);
        });
      });
      displayPolygons();
    }
  } catch (error) {
    console.log("Куда собрался? Я с тобой ещё не закончил.");
  }
}

function getCookie(name) {
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        window.csrfToken = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return;
}
