function getRecipeImage(recipe) {
  return (
    recipe.cover_url ||
    recipe.cover_image || // backward compatibility
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600"
  );
}

function renderRecipeCard(recipe, container) {
  const card = document.createElement("article");
  card.className = "recipe-card";
  card.innerHTML = `
    <img class="recipe-card__image" src="${getRecipeImage(recipe)}" alt="" loading="lazy">
    <div class="recipe-card__body">
      <h3 class="recipe-card__title">${recipe.title}</h3>
      <button type="button" class="btn btn-primary btn-sm">Смотреть</button>
    </div>
  `;
  card.querySelector("button").addEventListener("click", () => viewRecipe(recipe.id));
  container.appendChild(card);
}

async function loadAllRecipes() {
  try {
    const response = await fetch(`${API_BASE}/recipes`);
    const data = await response.json();
    const recipes = data.recipes.filter((r) => r.is_published);

    const container = document.getElementById("all-recipes-container");
    container.innerHTML = "";

    if (!recipes.length) {
      container.innerHTML = '<p class="text-muted">Пока нет опубликованных рецептов.</p>';
      return;
    }

    recipes.forEach((recipe) => {
      renderRecipeCard(recipe, container);
    });
  } catch (error) {
    console.error("Error loading recipes:", error);
  }
}

async function loadTags() {
  try {
    const response = await fetch(`${API_BASE}/tags`);
    const data = await response.json();
    const dropdown = document.getElementById("tag-dropdown");
    data.tags.forEach((tag) => {
      const option = document.createElement("option");
      option.value = tag;
      option.textContent = tag;
      dropdown.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading tags:", error);
  }
}

async function searchRecipes() {
  const query = document.getElementById("search-bar").value.trim();
  const selectedTag = document.getElementById("tag-dropdown").value;
  const params = new URLSearchParams();
  if (query) params.append("query", query);
  if (selectedTag !== "none") params.append("tags", selectedTag);

  try {
    const response = await fetch(`${API_BASE}/recipes/search?${params.toString()}`);
    const data = await response.json();
    const section = document.getElementById("search-results-section");
    const container = document.getElementById("search-results");
    container.innerHTML = "";
    section.classList.remove("hidden");

    if (!data.recipes.length) {
      container.innerHTML = '<p class="text-muted">Ничего не найдено.</p>';
      return;
    }

    data.recipes.forEach((recipe) => renderRecipeCard(recipe, container));
  } catch (error) {
    console.error("Error searching:", error);
  }
}

function viewRecipe(recipeId) {
  window.location.href = `/recipe.html?id=${recipeId}`;
}

document.addEventListener("DOMContentLoaded", () => {
  loadAllRecipes();
  loadTags();
});
