if (!requireAuth()) throw new Error("auth required");
document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const recipeId = params.get('recipe_id');
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (!recipeId || !userId || !token) {
        document.getElementById('recipe-details').innerHTML = '<p>Recipe not found or user not authenticated.</p>';
        return;
    }

    try {
        const [recipeRes, bookRes] = await Promise.all([
            fetch(`${API_BASE}/recipes/${recipeId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(`${API_BASE}/recipe-book/${userId}/recipes/${recipeId}/details`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
        ]);

        if (!recipeRes.ok || !bookRes.ok) {
            throw new Error('Failed to fetch recipe or book details');
        }

        const recipe = await recipeRes.json();
        const bookDetails = await bookRes.json();

        const missingIngredients = new Set(bookDetails.missing_ingredients);
        const completedSteps = new Set(bookDetails.completed_steps);

        const container = document.getElementById('recipe-details');
        container.innerHTML = '';

        const title = document.createElement('h2');
        title.textContent = recipe.title;
        container.appendChild(title);

        // Ingredients
        const ingHeader = document.createElement('h3');
        ingHeader.textContent = 'Ingredients:';
        container.appendChild(ingHeader);

        const ingList = document.createElement('ul');
        ingList.id = 'ingredient-list';
        recipe.ingredients.forEach(ing => {
            const li = document.createElement('li');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.dataset.ingredientName = ing.name;
            checkbox.checked = !missingIngredients.has(ing.name);
            checkbox.addEventListener('change', async () => {
                const action = checkbox.checked ? 'unmissing' : 'missing';
                await fetch(`${API_BASE}/recipe-book/${userId}/ingredients/${recipeId}/${ing.name}/${action}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            });

            li.appendChild(checkbox);
            li.append(` ${ing.name}`);
            ingList.appendChild(li);
        });
        container.appendChild(ingList);

        // Steps
        const stepHeader = document.createElement('h3');
        stepHeader.textContent = 'Steps:';
        container.appendChild(stepHeader);

        const stepList = document.createElement('ol');
        stepList.id = 'step-list';
        recipe.steps.forEach((step, idx) => {
            const li = document.createElement('li');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.dataset.stepIndex = idx;
            checkbox.checked = completedSteps.has(idx);
            checkbox.addEventListener('change', async () => {
                const action = checkbox.checked ? 'complete' : 'uncomplete';
                await fetch(`${API_BASE}/recipe-book/${userId}/steps/${recipeId}/${idx}/${action}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            });

            li.appendChild(checkbox);

            const description = document.createElement('span');
            description.textContent = ` ${step.description}`;
            li.appendChild(description);

            if (step.contents && step.contents.length > 0) {
                step.contents.forEach(content => {
                    if (content.url) {
                        const img = document.createElement('img');
                        img.src = content.url;
                        img.alt = `Step ${idx + 1}`;
                        img.style.maxWidth = '200px';
                        img.style.display = 'block';
                        img.style.marginTop = '5px';
                        li.appendChild(img);

                        const link = document.createElement('a');
                        link.href = content.url;
                        link.textContent = 'Открыть изображение';
                        link.target = '_blank';
                        link.style.display = 'block';
                        link.style.marginBottom = '5px';
                        li.appendChild(link);
                    }
                });
            }

            stepList.appendChild(li);
        });
        container.appendChild(stepList);

        // Tags
        const tagHeader = document.createElement('h3');
        tagHeader.textContent = 'Tags:';
        container.appendChild(tagHeader);

        const tagPara = document.createElement('p');
        tagPara.textContent = recipe.tags.join(', ');
        container.appendChild(tagPara);

        // Remove from book button
        const removeButton = document.createElement('button');
        removeButton.id = 'remove-from-book';
        removeButton.textContent = 'Remove from My Book';
        removeButton.addEventListener('click', async () => {
            await fetch(`${API_BASE}/recipe-book/${userId}/remove?recipe_id=${recipeId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            window.location.href = '/dashboard.html';
        });
        container.appendChild(removeButton);

    } catch (err) {
        console.error('Error loading recipe from book:', err);
        document.getElementById('recipe-details').innerHTML = '<p>Failed to load recipe.</p>';
    }
});
