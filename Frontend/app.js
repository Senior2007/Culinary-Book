function requireAuth(redirectTo = "/login.html") {
  if (!localStorage.getItem("token")) {
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("is_admin");
  localStorage.removeItem("is_banned");
  window.location.href = "/index.html";
}

function setCurrentUserFlags(data) {
  localStorage.setItem("is_admin", data.is_admin ? "true" : "false");
  localStorage.setItem("is_banned", data.is_banned ? "true" : "false");
}

function isCurrentAdmin() {
  return localStorage.getItem("is_admin") === "true";
}

function isCurrentBanned() {
  return localStorage.getItem("is_banned") === "true";
}

function updateNav() {
  const token = localStorage.getItem("token");
  const nav = document.getElementById("site-nav");
  if (!nav) return;

  if (token) {
    const adminLink = isCurrentAdmin() ? '<a href="/admin.html">Админ</a>' : "";
    nav.innerHTML = `
      <a href="/dashboard.html">Кабинет</a>
      <a href="/create_recipe.html">Новый рецепт</a>
      <a href="/raiting_page.html">Рейтинг</a>
      ${adminLink}
      <button type="button" class="btn btn-secondary btn-sm" id="nav-logout">Выйти</button>
    `;
    document.getElementById("nav-logout")?.addEventListener("click", logout);
  } else {
    nav.innerHTML = `
      <a href="/login.html">Вход</a>
      <a href="/register.html">Регистрация</a>
      <a href="/raiting_page.html">Рейтинг</a>
    `;
  }
}

async function refreshCurrentUser() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const res = await fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    const data = await res.json();
    localStorage.setItem("user_id", data.user_id);
    setCurrentUserFlags(data);
    updateNav();
    return data;
  } catch (_) {
    return null;
  }
}

async function displayUserRatingBadge() {
  const userId = localStorage.getItem("user_id");
  const token = localStorage.getItem("token");
  const el = document.getElementById("user-rating-badge");
  if (!el || !userId || !token) return;

  try {
    const res = await fetch(`${API_BASE}/ratings/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      el.textContent = `★ ${data.rating}`;
      el.classList.remove("hidden");
    }
  } catch (_) {}
}

document.addEventListener("DOMContentLoaded", () => {
  updateNav();
  refreshCurrentUser();
  displayUserRatingBadge();
});
