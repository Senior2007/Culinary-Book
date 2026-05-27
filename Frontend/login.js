document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const alertEl = document.getElementById("login-alert");
  alertEl.classList.add("hidden");

  const login = document.getElementById("login").value.trim();
  const password = document.getElementById("password").value;

  try {
    const response = await fetch(`${API_BASE}/authenticate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password }),
    });

    const data = await response.json();
    if (!response.ok) {
      alertEl.textContent = data.detail || "Ошибка входа";
      alertEl.classList.remove("hidden");
      return;
    }

    localStorage.setItem("token", data.token);
    localStorage.setItem("user_id", data.user_id);
    setCurrentUserFlags(data);
    window.location.href = "/dashboard.html";
  } catch (error) {
    console.error(error);
    alertEl.textContent = "Не удалось выполнить вход.";
    alertEl.classList.remove("hidden");
  }
});
