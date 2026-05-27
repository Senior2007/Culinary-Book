const strengthMeter = document.getElementById("strength-meter");
const strengthHint = document.getElementById("strength-hint");
const passwordInput = document.getElementById("password");
const confirmInput = document.getElementById("password-confirm");
const confirmError = document.getElementById("confirm-error");

function checkPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return score;
}

function updateStrengthUI(password) {
  strengthMeter.className = "strength-meter";
  if (!password) {
    strengthHint.textContent = "Мин. 8 символов, заглавная, строчная буква и цифра";
    return false;
  }
  const score = checkPasswordStrength(password);
  if (score < 3) {
    strengthMeter.classList.add("strength-weak");
    strengthHint.textContent = "Слабый пароль";
    return false;
  }
  if (score < 4) {
    strengthMeter.classList.add("strength-medium");
    strengthHint.textContent = "Средний пароль";
    return true;
  }
  strengthMeter.classList.add("strength-strong");
  strengthHint.textContent = "Надёжный пароль";
  return true;
}

passwordInput.addEventListener("input", () => updateStrengthUI(passwordInput.value));

confirmInput.addEventListener("input", () => {
  const mismatch = confirmInput.value && confirmInput.value !== passwordInput.value;
  confirmError.classList.toggle("hidden", !mismatch);
});

document.getElementById("register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const alertEl = document.getElementById("register-alert");
  alertEl.classList.add("hidden");

  const login = document.getElementById("login").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = passwordInput.value;
  const confirm = confirmInput.value;

  if (password !== confirm) {
    confirmError.classList.remove("hidden");
    return;
  }

  if (!updateStrengthUI(password)) {
    alertEl.textContent = "Пароль слишком слабый. Нужны: 8+ символов, A-Z, a-z, 0-9.";
    alertEl.classList.remove("hidden");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login, password, email }),
    });

    const data = await response.json();
    if (!response.ok) {
      alertEl.textContent = data.detail || "Ошибка регистрации";
      alertEl.classList.remove("hidden");
      return;
    }

    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("token", data.token);
    setCurrentUserFlags(data);
    window.location.href = "/dashboard.html";
  } catch (error) {
    console.error(error);
    alertEl.textContent = "Не удалось выполнить регистрацию. Попробуйте позже.";
    alertEl.classList.remove("hidden");
  }
});
