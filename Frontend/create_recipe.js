if (!requireAuth()) throw new Error("auth required");

let recipeId = null;
const token = localStorage.getItem("token");

document.addEventListener("DOMContentLoaded", async () => {
    if (typeof refreshCurrentUser === "function") {
        await refreshCurrentUser();
    }

    const urlParams = new URLSearchParams(window.location.search);
    recipeId = urlParams.get("recipe_id");

    if (recipeId) {
        await fetchRecipeDetails(recipeId);
    }

    document.getElementById("create-recipe-form").addEventListener("submit", handleSaveRecipe);
    document.getElementById("add-ingredient").addEventListener("click", handleAddIngredient);
    document.getElementById("add-step").addEventListener("click", handleAddStep);
    document.getElementById("add-tag").addEventListener("click", handleAddTag);
    document.getElementById("publish-recipe").addEventListener("click", handlePublishRecipe);
    document.getElementById("delete-recipe").addEventListener("click", handleDeleteRecipe);
});

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

async function handleSaveRecipe(event) {
    event.preventDefault();
    const title = document.getElementById("title").value.trim();
    if (!title) return alert("Title is required");
    const cover_url = document.getElementById("cover-url").value.trim() || null;

    const method = recipeId ? "PATCH" : "POST";
    const url = recipeId
        ? `${API_BASE}/recipes/${recipeId}`
        : `${API_BASE}/recipes`;

    try {
        const res = await fetch(url, {
            method,
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, cover_url }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to save recipe");

        recipeId = data.recipe_id;
        alert("Recipe saved!");
    } catch (err) {
        alert(err.message);
    }
}

async function handleDeleteRecipe() {
    if (!recipeId) return alert("Recipe not created yet");

    if (!confirm("Are you sure you want to delete this recipe?")) return;

    try {
        const res = await fetch(`${API_BASE}/recipes/${recipeId}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Failed to delete recipe");
        }

        alert("Recipe deleted");
        window.location.href = "/dashboard.html";
    } catch (err) {
        alert(err.message);
    }
}

function createListItem(text, onDelete) {
    const li = document.createElement("li");
    li.textContent = text;
    const btn = document.createElement("button");
    btn.textContent = "×";
    btn.style.marginLeft = "10px";
    btn.addEventListener("click", onDelete);
    li.appendChild(btn);
    return li;
}

function getStepIndex(element) {
    return Array.from(document.getElementById("steps-list").children).indexOf(element);
}

function createStepListItem(step) {
    const li = document.createElement("li");

    const editor = document.createElement("div");
    editor.className = "step-editor";

    const textarea = document.createElement("textarea");
    textarea.rows = 2;
    textarea.value = step.description;
    editor.appendChild(textarea);

    const actions = document.createElement("div");
    actions.className = "btn-group mt-1";

    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "btn btn-secondary btn-sm";
    saveBtn.textContent = "Сохранить текст";
    saveBtn.addEventListener("click", () => handleUpdateStep(li, textarea));

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "btn btn-danger btn-sm";
    deleteBtn.textContent = "Удалить шаг";
    deleteBtn.addEventListener("click", () => handleDeleteItem("steps", step.description, li));

    actions.append(saveBtn, deleteBtn);
    editor.appendChild(actions);

    (step.contents || []).forEach((content, imageIndex) => {
        if (!content.url) return;

        const imageWrap = document.createElement("div");
        imageWrap.className = "step-image";

        const img = document.createElement("img");
        img.src = content.url;
        img.alt = `Step image ${imageIndex + 1}`;

        const deleteImageBtn = document.createElement("button");
        deleteImageBtn.type = "button";
        deleteImageBtn.className = "btn btn-danger btn-sm";
        deleteImageBtn.textContent = "Удалить фото";
        deleteImageBtn.addEventListener("click", () => {
            const currentImageIndex = Array.from(editor.querySelectorAll(".step-image")).indexOf(imageWrap);
            handleDeleteStepImage(li, currentImageIndex, imageWrap);
        });

        imageWrap.append(img, deleteImageBtn);
        editor.appendChild(imageWrap);
    });

    li.appendChild(editor);
    return li;
}

async function handleAddIngredient() {
    const name = document.getElementById("ingredient").value.trim();
    if (!name || !recipeId) return alert("Enter ingredient and save recipe first");

    try {
        const url = `${API_BASE}/recipes/${recipeId}/ingredients`;
        const res = await fetch(url, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, ingredient_id: generateUUID() }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add ingredient");

        const li = createListItem(name, () => handleDeleteItem("ingredients", name, li));
        document.getElementById("ingredients-list").appendChild(li);
        document.getElementById("ingredient").value = "";
    } catch (err) {
        alert(err.message);
    }
}

async function handleAddStep() {
    const description = document.getElementById("step-description").value.trim();
    const imageUrl = document.getElementById("step-image").value.trim();
    if (!description || !recipeId) return alert("Enter step and save recipe first");

    try {
        const url = `${API_BASE}/recipes/${recipeId}/steps`;
        const res = await fetch(url, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ description }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add step");

        const stepIndex = document.getElementById("steps-list").children.length;
        const contents = [];
        if (imageUrl) {
            const imageAdded = await addImageToStep(stepIndex, imageUrl);
            if (imageAdded) contents.push({ url: imageUrl });
            document.getElementById("step-image").value = "";
        }

        const li = createStepListItem({ description, contents });
        document.getElementById("steps-list").appendChild(li);
        document.getElementById("step-description").value = "";
    } catch (err) {
        alert(err.message);
    }
}

async function addImageToStep(index, imageUrl) {
    try {
        const url = `${API_BASE}/recipes/${recipeId}/steps/${index}/images`;
        const res = await fetch(url, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image_url: imageUrl })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add image to step");
        return true;
    } catch (err) {
        alert(err.message);
        return false;
    }
}

async function handleUpdateStep(element, textarea) {
    const stepIndex = getStepIndex(element);
    const description = textarea.value.trim();
    if (stepIndex < 0) return alert("Step not found");
    if (!description) return alert("Step text is required");

    try {
        const params = new URLSearchParams({ description });
        const res = await fetch(`${API_BASE}/recipes/${recipeId}/steps/${stepIndex}/description?${params.toString()}`, {
            method: "PUT",
            headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to update step");
        alert("Step updated");
    } catch (err) {
        alert(err.message);
    }
}

async function handleDeleteStepImage(element, imageIndex, imageElement) {
    const stepIndex = getStepIndex(element);
    if (stepIndex < 0) return alert("Step not found");
    if (!confirm("Удалить фото из шага?")) return;

    try {
        const res = await fetch(`${API_BASE}/recipes/${recipeId}/steps/${stepIndex}/images/${imageIndex}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to delete image");
        imageElement.remove();
    } catch (err) {
        alert(err.message);
    }
}

async function handleAddTag() {
    const name = document.getElementById("tag").value.trim();
    if (!name || !recipeId) return alert("Enter tag and save recipe first");

    try {
        const url = `${API_BASE}/recipes/${recipeId}/tags`;
        const res = await fetch(url, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to add tag");

        const li = createListItem(name, () => handleDeleteItem("tags", name, li));
        document.getElementById("tags-list").appendChild(li);
        document.getElementById("tag").value = "";
    } catch (err) {
        alert(err.message);
    }
}

async function handleDeleteItem(type, identifier, element) {
    try {
        let url;
        if (type === "tags") {
            url = `${API_BASE}/recipes/${recipeId}/tags/${encodeURIComponent(identifier)}`;
        } else if (type === "steps") {
            const stepIndex = Array.from(document.getElementById("steps-list").children).indexOf(element);
            url = `${API_BASE}/recipes/${recipeId}/steps/${stepIndex}`;
        } else if (type === "ingredients") {
            url = `${API_BASE}/recipes/${recipeId}/ingredients/${encodeURIComponent(identifier)}`;
        } else {
            throw new Error("Invalid type for deletion");
        }

        const res = await fetch(url, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || `Failed to delete ${type.slice(0, -1)}`);

        element.remove();
    } catch (err) {
        alert(err.message);
    }
}

async function handlePublishRecipe() {
    if (!recipeId) return alert("Save recipe first");
    if (isCurrentBanned()) return alert("Ваш аккаунт забанен: публикация рецептов недоступна.");

    try {
        const res = await fetch(`${API_BASE}/recipes/${recipeId}/publish`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to publish recipe");

        alert("Recipe published!");
        window.location.href = "/"; // Redirect to homepage to see the published recipe
    } catch (err) {
        alert(err.message);
    }
}

async function fetchRecipeDetails(id) {
    try {
        const res = await fetch(`${API_BASE}/recipes/${id}`, {
            headers: { Authorization: `Bearer ${token}` },
        });

        const recipe = await res.json();
        if (!res.ok) throw new Error(recipe.detail || "Failed to load recipe");

        document.getElementById("title").value = recipe.title;
        if (recipe.cover_url) {
            document.getElementById("cover-url").value = recipe.cover_url;
        }

        recipe.ingredients.forEach(ing => {
            const li = createListItem(ing.name, () => handleDeleteItem("ingredients", ing.name, li));
            document.getElementById("ingredients-list").appendChild(li);
        });

        recipe.steps.forEach((step) => {
            document.getElementById("steps-list").appendChild(createStepListItem(step));
        });

        recipe.tags.forEach(tag => {
            const li = createListItem(tag, () => handleDeleteItem("tags", tag, li));
            document.getElementById("tags-list").appendChild(li);
        });

        if (recipe.is_published && !isCurrentAdmin()) {
            disableEditing();
        }
    } catch (err) {
        alert(err.message);
    }
}

function disableEditing() {
    document.getElementById("published-notice")?.classList.remove("hidden");
    document.getElementById("title").disabled = true;
    document.getElementById("ingredient").closest(".search-bar")?.classList.add("hidden");
    document.getElementById("step-description").closest(".form-group")?.classList.add("hidden");
    document.getElementById("step-image").closest(".form-group")?.classList.add("hidden");
    document.getElementById("add-step")?.classList.add("hidden");
    document.getElementById("tag").closest(".search-bar")?.classList.add("hidden");
    document.querySelector("#create-recipe-form button[type='submit']")?.classList.add("hidden");
    document.getElementById("publish-recipe")?.classList.add("hidden");
    document.querySelectorAll("#ingredients-list button, #steps-list button, #tags-list button").forEach((b) => {
        b.classList.add("hidden");
    });
    document.querySelectorAll("#steps-list textarea").forEach((field) => {
        field.disabled = true;
    });
}
