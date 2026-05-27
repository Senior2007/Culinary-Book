if (!requireAuth()) throw new Error("auth required");

const token = localStorage.getItem("token");
const userId = localStorage.getItem("user_id");

document.getElementById("create-recipe-btn").addEventListener("click", () => {
  window.location.href = "/create_recipe.html";
});

document.getElementById("view-missing-ingredients-btn").addEventListener("click", () => {
  window.location.href = "/missing_ingridients.html";
});

async function deleteRecipe(recipeId, title) {
  if (!confirm(`Удалить рецепт «${title}»? Это действие нельзя отменить.`)) return;

  try {
    const res = await fetch(`${API_BASE}/recipes/${recipeId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Не удалось удалить");
    }
    await fetchAndDisplayRecipes();
  } catch (err) {
    alert(err.message);
  }
}

async function fetchAndDisplayRecipes() {
  const list = document.getElementById("my-recipes-list");
  const empty = document.getElementById("my-recipes-empty");
  list.innerHTML = "";

  const response = await fetch(`${API_BASE}/recipes/author/${userId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    console.error("Failed to fetch recipes");
    return;
  }

  const data = await response.json();
  if (!data.recipes.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  data.recipes.forEach((recipe) => {
    const li = document.createElement("li");
    li.className = "recipe-list__item";

    const titleSpan = document.createElement("span");
    titleSpan.className = "recipe-list__title";
    titleSpan.textContent = recipe.title;
    titleSpan.addEventListener("click", () => {
      window.location.href = `/create_recipe.html?recipe_id=${recipe.id}`;
    });

    const badge = document.createElement("span");
    badge.className = recipe.is_published ? "badge badge-published" : "badge badge-draft";
    badge.textContent = recipe.is_published ? "Опубликован" : "Черновик";

    const actions = document.createElement("div");
    actions.className = "btn-group";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "btn btn-secondary btn-sm";
    editBtn.textContent = "Изменить";
    editBtn.addEventListener("click", () => {
      window.location.href = `/create_recipe.html?recipe_id=${recipe.id}`;
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "btn btn-danger btn-sm";
    deleteBtn.textContent = "Удалить";
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteRecipe(recipe.id, recipe.title);
    });

    actions.append(editBtn, deleteBtn);
    li.append(titleSpan, badge, actions);
    list.appendChild(li);
  });
}

async function fetchAndDisplayBookRecipes() {
  const list = document.getElementById("book-recipes-list");
  const empty = document.getElementById("book-recipes-empty");
  list.innerHTML = "";

  try {
    const response = await fetch(`${API_BASE}/recipe-book/${userId}/recipes`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch recipe book");

    const data = await response.json();
    if (!data.recipes.length) {
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");

    data.recipes.forEach((recipe) => {
      const li = document.createElement("li");
      li.className = "recipe-list__item";
      const titleSpan = document.createElement("span");
      titleSpan.className = "recipe-list__title";
      titleSpan.textContent = recipe.title;
      titleSpan.addEventListener("click", () => {
        window.location.href = `/book_recipe.html?recipe_id=${recipe.id}`;
      });
      li.appendChild(titleSpan);
      list.appendChild(li);
    });
  } catch (error) {
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchAndDisplayRecipes();
  fetchAndDisplayBookRecipes();
});
