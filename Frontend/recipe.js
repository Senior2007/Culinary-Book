const token = localStorage.getItem("token");
const userId = localStorage.getItem("user_id");
let currentRecipe = null;
let currentRecipeId = null;

async function loadRecipeDetails() {
  const params = new URLSearchParams(window.location.search);
  const recipeId = params.get("id");
  currentRecipeId = recipeId;

  if (!recipeId) {
    document.getElementById("recipe-details").innerHTML =
      '<p class="alert alert-error">Рецепт не найден.</p>';
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/recipes/${recipeId}`);
    if (!response.ok) throw new Error("Failed to fetch");
    const recipe = await response.json();
    currentRecipe = recipe;

    const container = document.getElementById("recipe-details");
    container.innerHTML = "";

    const title = document.createElement("h2");
    title.textContent = recipe.title;

    const author = document.createElement("a");
    author.className = "author-link";
    author.href = `/profile.html?id=${recipe.author_id}`;
    author.textContent = `Автор: загрузка…`;
    loadAuthorName(recipe.author_id, author);

    const ingredientsTitle = document.createElement("h3");
    ingredientsTitle.textContent = "Ингредиенты";
    const ingredientsList = document.createElement("ul");
    recipe.ingredients.forEach((ing) => {
      const li = document.createElement("li");
      li.textContent = ing.name;
      ingredientsList.appendChild(li);
    });

    const stepsTitle = document.createElement("h3");
    stepsTitle.textContent = "Шаги";
    const stepsList = document.createElement("ol");
    recipe.steps.forEach((step, index) => {
      const li = document.createElement("li");
      const desc = document.createElement("p");
      desc.textContent = step.description;
      li.appendChild(desc);
      (step.contents || []).forEach((content) => {
        if (content.url) {
          const img = document.createElement("img");
          img.src = content.url;
          img.alt = `Шаг ${index + 1}`;
          li.appendChild(img);
        }
      });
      stepsList.appendChild(li);
    });

    const tagsTitle = document.createElement("h3");
    tagsTitle.textContent = "Теги";
    const tagsText = document.createElement("p");
    tagsText.textContent = recipe.tags.join(", ") || "—";

    container.append(title, author, ingredientsTitle, ingredientsList, stepsTitle, stepsList, tagsTitle, tagsText);

    if (token && userId && recipe.author_id !== userId && !isCurrentBanned()) {
      await setupAddToBook(recipeId);
      document.getElementById("comment-form-section").classList.remove("hidden");
    } else if (token && isCurrentBanned()) {
      const hint = document.getElementById("comment-login-hint");
      hint.textContent = "Ваш аккаунт забанен: комментарии недоступны.";
      hint.classList.remove("hidden");
    } else if (!token) {
      document.getElementById("comment-login-hint").classList.remove("hidden");
    }

    await loadComments(recipeId);
  } catch (error) {
    console.error(error);
    document.getElementById("recipe-details").innerHTML =
      '<p class="alert alert-error">Ошибка загрузки рецепта.</p>';
  }
}

async function loadAuthorName(authorId, el) {
  try {
    const res = await fetch(`${API_BASE}/users/${authorId}/profile`);
    if (res.ok) {
      const p = await res.json();
      el.textContent = `Автор: ${p.login}`;
    }
  } catch (_) {
    el.textContent = "Автор";
  }
}

async function setupAddToBook(recipeId) {
  const bookResponse = await fetch(`${API_BASE}/recipe-book/${userId}/recipes`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!bookResponse.ok) return;
  const bookData = await bookResponse.json();
  const isInBook = bookData.recipes.some((r) => r.id === recipeId);
  if (!isInBook) {
    document.getElementById("add-to-book-section").classList.remove("hidden");
    document.getElementById("add-to-book-button").addEventListener("click", () =>
      addRecipeToBook(userId, recipeId)
    );
  }
}

async function addRecipeToBook(uid, recipeId) {
  try {
    const response = await fetch(`${API_BASE}/recipe-book/${uid}/add?recipe_id=${recipeId}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Ошибка");
    alert("Рецепт добавлен в вашу книгу!");
    document.getElementById("add-to-book-section").classList.add("hidden");
  } catch (err) {
    alert("Ошибка: " + err.message);
  }
}

async function loadComments(recipeId) {
  const list = document.getElementById("comments-list");
  list.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/recipes/${recipeId}/comments`);
    const data = await res.json();

    if (!data.comments.length) {
      list.innerHTML = '<p class="text-muted">Пока нет комментариев. Будьте первым!</p>';
      return;
    }

    data.comments.forEach((c) => {
      const div = document.createElement("article");
      div.className = "comment";

      const header = document.createElement("div");
      header.className = "comment__header";
      header.innerHTML = `
        <span class="comment__author">
          <a href="/profile.html?id=${c.user_id}">${c.author_login}</a>
        </span>
        <span class="comment__date">${new Date(c.created_at).toLocaleString("ru-RU")}</span>
      `;

      const text = document.createElement("p");
      text.className = "comment__text";
      text.textContent = c.text;

      div.append(header, text);

      if (c.image_urls?.length) {
        const imgs = document.createElement("div");
        imgs.className = "comment__images";
        c.image_urls.forEach((url) => {
          const img = document.createElement("img");
          img.src = url;
          img.alt = "Фото к комментарию";
          imgs.appendChild(img);
        });
        div.appendChild(imgs);
      }

      if (userId && (c.user_id === userId || isCurrentAdmin())) {
        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "btn btn-danger btn-sm mt-1";
        delBtn.textContent = "Удалить";
        delBtn.addEventListener("click", () => deleteComment(c.id));
        div.appendChild(delBtn);
      }

      list.appendChild(div);
    });
  } catch (e) {
    list.innerHTML = '<p class="text-muted">Не удалось загрузить комментарии.</p>';
  }
}

async function deleteComment(commentId) {
  if (!confirm("Удалить комментарий?")) return;
  const res = await fetch(`${API_BASE}/comments/${commentId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.ok) await loadComments(currentRecipeId);
  else alert("Не удалось удалить");
}

document.getElementById("comment-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isCurrentBanned()) return alert("Ваш аккаунт забанен: комментарии недоступны.");
  const text = document.getElementById("comment-text").value.trim();
  const imageUrl = document.getElementById("comment-image").value.trim();
  const image_urls = imageUrl ? [imageUrl] : [];

  try {
    const res = await fetch(`${API_BASE}/recipes/${currentRecipeId}/comments`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text, image_urls }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Ошибка");
    document.getElementById("comment-form").reset();
    await loadComments(currentRecipeId);
  } catch (err) {
    alert(err.message);
  }
});

document.addEventListener("DOMContentLoaded", async () => {
  if (typeof refreshCurrentUser === "function") {
    await refreshCurrentUser();
  }
  loadRecipeDetails();
});
