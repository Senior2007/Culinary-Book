async function loadProfile() {
  const params = new URLSearchParams(window.location.search);
  const userId = params.get("id");
  const container = document.getElementById("profile-content");

  if (!userId) {
    container.innerHTML = '<p class="alert alert-error">Пользователь не указан.</p>';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/${userId}/profile`);
    if (!res.ok) throw new Error("Not found");
    const profile = await res.json();

    const initial = (profile.login[0] || "?").toUpperCase();
    container.innerHTML = `
      <div class="profile-avatar">${initial}</div>
      <h1 class="section-title mb-0">${profile.login}</h1>
      <p class="profile-email">${profile.email}</p>
      <p class="user-badge" style="margin:1rem auto;display:inline-flex">★ Рейтинг: ${profile.rating}</p>
      <p class="mt-1"><a href="/index.html">← На главную</a></p>
    `;
    document.title = `${profile.login} — Culinary Book`;
  } catch (_) {
    container.innerHTML = '<p class="alert alert-error">Профиль не найден.</p>';
  }
}

document.addEventListener("DOMContentLoaded", loadProfile);
