if (!requireAuth()) throw new Error("auth required");

const token = localStorage.getItem("token");

function showAdminError(message) {
  const alertEl = document.getElementById("admin-alert");
  alertEl.textContent = message;
  alertEl.classList.remove("hidden");
}

async function adminFetch(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
  return data;
}

function makeBadge(text, className) {
  const badge = document.createElement("span");
  badge.className = `badge ${className}`;
  badge.textContent = text;
  return badge;
}

async function toggleBan(userId, shouldBan) {
  const action = shouldBan ? "ban" : "unban";
  await adminFetch(`${API_BASE}/admin/users/${userId}/${action}`, { method: "POST" });
  await loadUsers();
}

async function loadUsers() {
  const list = document.getElementById("admin-users-list");
  list.innerHTML = "";

  const data = await adminFetch(`${API_BASE}/admin/users`);
  data.users.forEach((user) => {
    const li = document.createElement("li");
    li.className = "recipe-list__item";

    const title = document.createElement("span");
    title.className = "recipe-list__title";
    title.textContent = `${user.login} (${user.email || "без email"})`;

    const badges = document.createElement("div");
    badges.className = "btn-group";
    if (user.is_admin) badges.appendChild(makeBadge("Админ", "badge-published"));
    if (user.is_banned) badges.appendChild(makeBadge("Бан", "badge-draft"));

    const actions = document.createElement("div");
    actions.className = "btn-group";
    if (!user.is_admin) {
      const banBtn = document.createElement("button");
      banBtn.type = "button";
      banBtn.className = user.is_banned ? "btn btn-secondary btn-sm" : "btn btn-danger btn-sm";
      banBtn.textContent = user.is_banned ? "Разбанить" : "Забанить";
      banBtn.addEventListener("click", () => toggleBan(user.user_id, !user.is_banned));
      actions.appendChild(banBtn);
    }

    li.append(title, badges, actions);
    list.appendChild(li);
  });
}

async function deleteRecipe(recipeId, title) {
  if (!confirm(`Удалить рецепт «${title}»?`)) return;
  await adminFetch(`${API_BASE}/recipes/${recipeId}`, { method: "DELETE" });
  await loadRecipes();
  await loadComments();
}

async function loadRecipes() {
  const list = document.getElementById("admin-recipes-list");
  list.innerHTML = "";

  const data = await fetch(`${API_BASE}/recipes`).then((res) => res.json());
  data.recipes.forEach((recipe) => {
    const li = document.createElement("li");
    li.className = "recipe-list__item";

    const title = document.createElement("span");
    title.className = "recipe-list__title";
    title.textContent = recipe.title;

    const badge = makeBadge(
      recipe.is_published ? "Опубликован" : "Черновик",
      recipe.is_published ? "badge-published" : "badge-draft"
    );

    const actions = document.createElement("div");
    actions.className = "btn-group";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "btn btn-secondary btn-sm";
    editBtn.textContent = "Изменить";
    editBtn.addEventListener("click", () => {
      window.location.href = `/create_recipe.html?recipe_id=${recipe.id}`;
    });

    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.className = "btn btn-secondary btn-sm";
    viewBtn.textContent = "Смотреть";
    viewBtn.addEventListener("click", () => {
      window.location.href = `/recipe.html?id=${recipe.id}`;
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "btn btn-danger btn-sm";
    deleteBtn.textContent = "Удалить";
    deleteBtn.addEventListener("click", () => deleteRecipe(recipe.id, recipe.title));

    actions.append(editBtn, viewBtn, deleteBtn);
    li.append(title, badge, actions);
    list.appendChild(li);
  });
}

function imageUrlsFromInput(value) {
  return value
    .split(/\n|,/)
    .map((url) => url.trim())
    .filter(Boolean);
}

async function saveComment(commentId, card) {
  const text = card.querySelector("[data-comment-text]").value.trim();
  const image_urls = imageUrlsFromInput(card.querySelector("[data-comment-images]").value);
  await adminFetch(`${API_BASE}/comments/${commentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, image_urls }),
  });
  await loadComments();
}

async function deleteComment(commentId) {
  if (!confirm("Удалить комментарий?")) return;
  await adminFetch(`${API_BASE}/comments/${commentId}`, { method: "DELETE" });
  await loadComments();
}

async function loadComments() {
  const list = document.getElementById("admin-comments-list");
  list.innerHTML = "";

  const data = await adminFetch(`${API_BASE}/admin/comments`);
  if (!data.comments.length) {
    list.innerHTML = '<p class="text-muted">Комментариев пока нет.</p>';
    return;
  }

  data.comments.forEach((comment) => {
    const card = document.createElement("article");
    card.className = "comment";

    const header = document.createElement("div");
    header.className = "comment__header";
    header.textContent = `${comment.author_login} к рецепту «${comment.recipe_title}»`;

    const text = document.createElement("textarea");
    text.dataset.commentText = "true";
    text.value = comment.text;
    text.rows = 3;

    const images = document.createElement("textarea");
    images.dataset.commentImages = "true";
    images.value = (comment.image_urls || []).join("\n");
    images.rows = 2;
    images.placeholder = "URL изображений, по одному в строке";

    const actions = document.createElement("div");
    actions.className = "btn-group mt-1";

    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "btn btn-primary btn-sm";
    saveBtn.textContent = "Сохранить";
    saveBtn.addEventListener("click", () => saveComment(comment.id, card));

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "btn btn-danger btn-sm";
    deleteBtn.textContent = "Удалить";
    deleteBtn.addEventListener("click", () => deleteComment(comment.id));

    actions.append(saveBtn, deleteBtn);
    card.append(header, text, images, actions);
    list.appendChild(card);
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await refreshCurrentUser();
    if (!isCurrentAdmin()) {
      showAdminError("Доступ только для администратора.");
      return;
    }

    await Promise.all([loadUsers(), loadRecipes(), loadComments()]);
  } catch (err) {
    showAdminError(err.message);
  }
});
