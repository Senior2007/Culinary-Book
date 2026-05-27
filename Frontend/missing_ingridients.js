
if (!requireAuth()) throw new Error("auth required");
async function fetchMissingIngredients() {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');
    const listEl = document.getElementById('missing-ingredients-list');
    listEl.innerHTML = '<li>Loading...</li>';

    try {
        const response = await fetch(`${API_BASE}/recipe-book/${userId}/missing-ingredients`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const ingredients = data.missing_ingredients;

        if (ingredients.length === 0) {
            listEl.innerHTML = '<li>No missing ingredients! 🎉</li>';
        } else {
            listEl.innerHTML = ingredients.map(name => `<li>${name}</li>`).join('');
        }
    } catch (error) {
        console.error('Error fetching missing ingredients:', error);
        listEl.innerHTML = '<li>Error loading missing ingredients.</li>';
    }
}

document.getElementById('refresh-btn').addEventListener('click', fetchMissingIngredients);

document.addEventListener('DOMContentLoaded', fetchMissingIngredients);
