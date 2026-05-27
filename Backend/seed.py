"""Populate MongoDB with demo users, recipes, and comments."""

import hashlib
import os
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from Domain.Entities.Recipe.Recipe import Recipe, Tag, Ingredient, Step
from Domain.Entities.Recipe.RecipeContent import RecipeContent
from Domain.Entities.Recipe.Comment import Comment
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.User.User import User
from Domain.Entities.RecipeBook.RecipeBook import Book

DEMO_PASSWORD = "Demo1234!"
ADMIN_ID = "00000000-0000-4000-8000-000000000001"
ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@culinary-book.local")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin1234!")

def img(url: str, w: int = 1200) -> str:
    """
    Make Unsplash images more reliably renderable across browsers/CDNs.
    - Force https
    - Add basic formatting params
    """
    if "upload.wikimedia.org" in url:
        return url
    base = url.split("?")[0]
    return f"{base}?auto=format&fit=crop&w={w}&q=80"

USER_RATINGS = {
    "11111111-1111-4111-8111-111111111101": 320,
    "11111111-1111-4111-8111-111111111102": 220,
    "11111111-1111-4111-8111-111111111103": 175,
    "11111111-1111-4111-8111-111111111104": 300,
    "11111111-1111-4111-8111-111111111105": 410,
    "11111111-1111-4111-8111-111111111106": 350,
    "11111111-1111-4111-8111-111111111107": 280,
    "11111111-1111-4111-8111-111111111108": 260,
    "11111111-1111-4111-8111-111111111109": 190,
    "11111111-1111-4111-8111-111111111110": 240,
}

USERS = [
    ("11111111-1111-4111-8111-111111111101", "chef_anna", "anna@gmail.com"),
    ("11111111-1111-4111-8111-111111111102", "baker_bob", "bob@yahoo.com"),
    ("11111111-1111-4111-8111-111111111103", "vegan_vika", "vika@outlook.com"),
    ("11111111-1111-4111-8111-111111111104", "pasta_pavel", "pavel@proton.me"),
    ("11111111-1111-4111-8111-111111111105", "sweet_sofia", "sofia@mail.ru"),
    ("11111111-1111-4111-8111-111111111106", "grill_greg", "greg@yandex.ru"),
    ("11111111-1111-4111-8111-111111111107", "soup_lena", "lena@icloud.com"),
    ("11111111-1111-4111-8111-111111111108", "spice_nina", "nina@fastmail.com"),
    ("11111111-1111-4111-8111-111111111109", "healthy_ivan", "ivan@tuta.com"),
    ("11111111-1111-4111-8111-111111111110", "home_maria", "maria@zoho.com"),
]

RECIPES = [
    {
        "id": "22222222-2222-4222-8222-222222222201",
        "title": "Классическая карбонара",
        "author": "11111111-1111-4111-8111-111111111101",
        "tags": ["итальянская", "паста", "ужин"],
        "ingredients": ["спагетти", "яйца", "пармезан", "бекон", "чёрный перец"],
        "steps": [
            ("Отварите спагетти в подсоленной воде до al dente.", "https://upload.wikimedia.org/wikipedia/commons/7/74/Spaghetti_Carbonara,_Trastevere,_Roma.jpg"),
            ("Обжарьте бекон до хрустящей корочки.", "https://upload.wikimedia.org/wikipedia/commons/7/74/Spaghetti_Carbonara,_Trastevere,_Roma.jpg"),
            ("Смешайте яйца с тертым пармезаном и перцем.", "https://upload.wikimedia.org/wikipedia/commons/7/74/Spaghetti_Carbonara,_Trastevere,_Roma.jpg"),
            ("Соедините пасту с беконом, снимите с огня и вмешайте яичную смесь.", "https://upload.wikimedia.org/wikipedia/commons/7/74/Spaghetti_Carbonara,_Trastevere,_Roma.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222202",
        "title": "Борщ украинский",
        "author": "11111111-1111-4111-8111-111111111107",
        "tags": ["суп", "обед", "традиционная"],
        "ingredients": ["свёкла", "капуста", "картофель", "говядина", "сметана"],
        "steps": [
            ("Сварите мясной бульон с лавровым листом.", "https://upload.wikimedia.org/wikipedia/commons/e/e0/Borshch2.jpg"),
            ("Натрите свёклу и морковь, обжарьте с томатной пастой.", "https://upload.wikimedia.org/wikipedia/commons/e/e0/Borshch2.jpg"),
            ("Добавьте капусту и картофель в бульон, варите 15 минут.", "https://upload.wikimedia.org/wikipedia/commons/e/e0/Borshch2.jpg"),
            ("Влейте зажарку, доведите до вкуса и подавайте со сметаной.", "https://upload.wikimedia.org/wikipedia/commons/e/e0/Borshch2.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222203",
        "title": "Салат Цезарь",
        "author": "11111111-1111-4111-8111-111111111109",
        "tags": ["салат", "обед", "быстро"],
        "ingredients": ["ромэн", "курица", "пармезан", "сухарики", "соус цезарь"],
        "steps": [
            ("Обжарьте куриное филе и нарежьте ломтиками.", "https://upload.wikimedia.org/wikipedia/commons/2/2e/GrilledCaesarSalad.jpg"),
            ("Порвите салат руками в миску.", "https://upload.wikimedia.org/wikipedia/commons/2/2e/GrilledCaesarSalad.jpg"),
            ("Добавьте соус, сухарики, пармезан и перемешайте.", "https://upload.wikimedia.org/wikipedia/commons/2/2e/GrilledCaesarSalad.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222204",
        "title": "Шоколадный брауни",
        "author": "11111111-1111-4111-8111-111111111105",
        "tags": ["десерт", "выпечка", "сладкое"],
        "ingredients": ["тёмный шоколад", "масло", "яйца", "сахар", "мука"],
        "steps": [
            ("Растопите шоколад с маслом на водяной бане.", "https://upload.wikimedia.org/wikipedia/commons/b/b4/Little-Debbie-Fudge-Brownies.jpg"),
            ("Взбейте яйца с сахаром до пышности.", "https://upload.wikimedia.org/wikipedia/commons/b/b4/Little-Debbie-Fudge-Brownies.jpg"),
            ("Соедините смеси, добавьте муку и выпекайте 25 минут при 180°C.", "https://upload.wikimedia.org/wikipedia/commons/b/b4/Little-Debbie-Fudge-Brownies.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222205",
        "title": "Стейк на гриле",
        "author": "11111111-1111-4111-8111-111111111106",
        "tags": ["мясо", "ужин", "гриль"],
        "ingredients": ["рибай", "соль", "перец", "чеснок", "розмарин"],
        "steps": [
            ("Достаньте мясо за 30 минут до готовки.", "https://upload.wikimedia.org/wikipedia/commons/8/8b/300_grams_Sirloin_Steak_(3690335768).jpg"),
            ("Разогрейте сковороду-гриль до максимума.", "https://upload.wikimedia.org/wikipedia/commons/8/8b/300_grams_Sirloin_Steak_(3690335768).jpg"),
            ("Жарьте по 3–4 минуты с каждой стороны для medium-rare.", "https://upload.wikimedia.org/wikipedia/commons/8/8b/300_grams_Sirloin_Steak_(3690335768).jpg"),
            ("Дайте отдохнуть 5 минут под фольгой перед нарезкой.", "https://upload.wikimedia.org/wikipedia/commons/8/8b/300_grams_Sirloin_Steak_(3690335768).jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222206",
        "title": "Блины тонкие",
        "author": "11111111-1111-4111-8111-111111111102",
        "tags": ["завтрак", "выпечка", "традиционная"],
        "ingredients": ["мука", "молоко", "яйца", "сахар", "масло"],
        "steps": [
            ("Смешайте все ингредиенты до однородного теста.", "https://upload.wikimedia.org/wikipedia/commons/3/30/Blini-Demidoff.jpg"),
            ("Выпекайте тонкие блины на разогретой сковороде.", "https://upload.wikimedia.org/wikipedia/commons/f/f4/Preparation_of_blins_or_blini.jpg"),
            ("Подавайте с вареньем или сметаной.", "https://upload.wikimedia.org/wikipedia/commons/3/30/Blini-Demidoff.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222207",
        "title": "Том Ям с креветками",
        "author": "11111111-1111-4111-8111-111111111108",
        "tags": ["суп", "азиатская", "острое"],
        "ingredients": ["креветки", "грибы", "лайм", "паста том ям", "кокосовое молоко"],
        "steps": [
            ("Вскипятите бульон с пастой том ям и лемонграссом.", "https://upload.wikimedia.org/wikipedia/commons/c/c8/Kaeng_som_kung.jpg"),
            ("Добавьте грибы и креветки, варите 5 минут.", "https://upload.wikimedia.org/wikipedia/commons/c/c8/Kaeng_som_kung.jpg"),
            ("Влейте кокосовое молоко и сок лайма перед подачей.", "https://upload.wikimedia.org/wikipedia/commons/c/c8/Kaeng_som_kung.jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222208",
        "title": "Будда-боул веганский",
        "author": "11111111-1111-4111-8111-111111111103",
        "tags": ["веган", "обед", "здоровое"],
        "ingredients": ["киноа", "нут", "авокадо", "шпинат", "тахини"],
        "steps": [
            ("Отварите киноа и запеките нут со специями.", "https://upload.wikimedia.org/wikipedia/commons/e/ed/Vegan_buffet_food_(109154310).jpg"),
            ("Разложите овощи и киноа в миску.", "https://upload.wikimedia.org/wikipedia/commons/e/ed/Vegan_buffet_food_(109154310).jpg"),
            ("Полейте соусом из тахини, лимона и чеснока.", "https://upload.wikimedia.org/wikipedia/commons/e/ed/Vegan_buffet_food_(109154310).jpg"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222209",
        "title": "Маргарита пицца",
        "author": "11111111-1111-4111-8111-111111111104",
        "tags": ["итальянская", "ужин", "выпечка"],
        "ingredients": ["тесто", "томатный соус", "моцарелла", "базилик", "оливковое масло"],
        "steps": [
            ("Раскатайте тесто и смажьте томатным соусом.", "https://upload.wikimedia.org/wikipedia/commons/d/d4/Margherita_Originale.JPG"),
            ("Выложите моцареллу и выпекайте 10–12 минут при 250°C.", "https://upload.wikimedia.org/wikipedia/commons/2/2e/Pizza_Margherita,_in_Naka-ku,_Nagoya_(2015.04.07).jpg"),
            ("Добавьте свежий базилик и оливковое масло.", "https://upload.wikimedia.org/wikipedia/commons/d/d4/Margherita_Originale.JPG"),
        ],
    },
    {
        "id": "22222222-2222-4222-8222-222222222210",
        "title": "Домашние пельмени",
        "author": "11111111-1111-4111-8111-111111111110",
        "tags": ["традиционная", "обед", "семейное"],
        "ingredients": ["мука", "фарш", "лук", "яйцо", "соль"],
        "steps": [
            ("Замесите крутое тесто и дайте отдохнуть 30 минут.", "https://upload.wikimedia.org/wikipedia/commons/4/49/Pelmeni.jpg"),
            ("Смешайте фарш с луком, солью и перцем.", "https://upload.wikimedia.org/wikipedia/commons/4/49/Pelmeni.jpg"),
            ("Слепите пельмени и варите в кипящей воде 7–8 минут.", "https://upload.wikimedia.org/wikipedia/commons/4/49/Pelmeni.jpg"),
        ],
    },
]

COMMENTS = [
    ("33333333-3333-4333-8333-333333333301", "22222222-2222-4222-8222-222222222201", "11111111-1111-4111-8111-111111111102", "Потрясающая карбонара! Сделал вчера — семья в восторге.", ["https://upload.wikimedia.org/wikipedia/commons/7/74/Spaghetti_Carbonara,_Trastevere,_Roma.jpg"]),
    ("33333333-3333-4333-8333-333333333302", "22222222-2222-4222-8222-222222222201", "11111111-1111-4111-8111-111111111105", "Добавила немного чеснока — получилось ещё вкуснее.", []),
    ("33333333-3333-4333-8333-333333333303", "22222222-2222-4222-8222-222222222202", "11111111-1111-4111-8111-111111111101", "Как у бабушки! Борщ получился насыщенным.", ["https://upload.wikimedia.org/wikipedia/commons/e/e0/Borshch2.jpg"]),
    ("33333333-3333-4333-8333-333333333304", "22222222-2222-4222-8222-222222222204", "11111111-1111-4111-8111-111111111110", "Брауни влажные внутри — идеальный рецепт!", ["https://upload.wikimedia.org/wikipedia/commons/b/b4/Little-Debbie-Fudge-Brownies.jpg"]),
    ("33333333-3333-4333-8333-333333333305", "22222222-2222-4222-8222-222222222205", "11111111-1111-4111-8111-111111111104", "Стейк получился сочным, спасибо за совет с отдыхом мяса.", []),
    ("33333333-3333-4333-8333-333333333306", "22222222-2222-4222-8222-222222222208", "11111111-1111-4111-8111-111111111109", "Отличный боул для meal prep на неделю.", ["https://upload.wikimedia.org/wikipedia/commons/e/ed/Vegan_buffet_food_(109154310).jpg"]),
    ("33333333-3333-4333-8333-333333333307", "22222222-2222-4222-8222-222222222209", "11111111-1111-4111-8111-111111111106", "Тесто поднялось отлично, пицца как в Неаполе.", []),
    ("33333333-3333-4333-8333-333333333308", "22222222-2222-4222-8222-222222222207", "11111111-1111-4111-8111-111111111103", "Остро и ароматно — добавила ещё лайма.", ["https://upload.wikimedia.org/wikipedia/commons/c/c8/Kaeng_som_kung.jpg"]),
]


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def ensure_admin_account(db) -> bool:
    """Create or refresh the built-in administrator account."""
    password_hash = _hash_password(ADMIN_PASSWORD)
    existing = await db["users"].find_one({"credentials.login": ADMIN_LOGIN})

    if existing:
        await db["users"].update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "credentials.password_hashes": [password_hash],
                    "credentials.email": ADMIN_EMAIL,
                    "credentials.is_admin": True,
                    "credentials.is_banned": False,
                }
            },
        )
        await db["ratings"].update_one(
            {"_id": existing["_id"]},
            {"$setOnInsert": {"rating": 0}},
            upsert=True,
        )
        return False

    await db["users"].replace_one(
        {"_id": ADMIN_ID},
        {
            "_id": ADMIN_ID,
            "credentials": {
                "id": ADMIN_ID,
                "login": ADMIN_LOGIN,
                "password_hashes": [password_hash],
                "email": ADMIN_EMAIL,
                "is_admin": True,
                "is_banned": False,
            },
            "authored_recipes": [],
            "recipe_book": {"user_id": ADMIN_ID, "entries": {}},
        },
        upsert=True,
    )
    await db["ratings"].replace_one(
        {"_id": ADMIN_ID},
        {"_id": ADMIN_ID, "rating": 0},
        upsert=True,
    )
    return True


async def seed_database(db) -> bool:
    """Returns True if seeding was performed."""
    if await db["users"].count_documents({}) > 0:
        return False

    password_hash = _hash_password(DEMO_PASSWORD)

    for user_id, login, email in USERS:
        uid = UUID(user_id)
        user = User(
            credentials=Credentials(
                id=uid,
                login=login,
                password_hashes=[password_hash],
                email=email,
            ),
            authored_recipes=[],
            recipe_book=Book(user_id=uid, entries={}),
        )
        await db["users"].replace_one(
            {"_id": user_id},
            {
                "_id": user_id,
                "credentials": {
                    "id": user_id,
                    "login": login,
                    "password_hashes": [password_hash],
                    "email": email,
                },
                "authored_recipes": [],
                "recipe_book": {"user_id": user_id, "entries": {}},
            },
            upsert=True,
        )
        await db["ratings"].replace_one(
            {"_id": user_id},
            {"_id": user_id, "rating": USER_RATINGS[user_id]},
            upsert=True,
        )

    for recipe_data in RECIPES:
        steps = [
            Step(
                description=desc,
                contents=[RecipeContent(url=img)] if img else [],
            )
            for desc, img in recipe_data["steps"]
        ]
        cover = steps[0].contents[0].url if steps and steps[0].contents else None
        recipe = Recipe(
            id=UUID(recipe_data["id"]),
            title=recipe_data["title"],
            author_id=UUID(recipe_data["author"]),
            ingredients=[Ingredient(name=n) for n in recipe_data["ingredients"]],
            steps=steps,
            tags=[Tag(name=t) for t in recipe_data["tags"]],
            is_published=True,
            cover_url=cover,
        )
        await db["recipes"].replace_one(
            {"_id": recipe_data["id"]},
            {
                "_id": recipe_data["id"],
                "title": recipe.title,
                "author_id": recipe_data["author"],
                "ingredients": [{"name": i.name} for i in recipe.ingredients],
                "steps": [
                    {
                        "description": s.description,
                        "contents": [{"url": c.url} for c in s.contents],
                    }
                    for s in recipe.steps
                ],
                "tags": [{"name": t.name} for t in recipe.tags],
                "is_published": True,
                "cover_url": cover,
            },
            upsert=True,
        )

    for comment_id, recipe_id, user_id, text, images in COMMENTS:
        comment = Comment(
            id=UUID(comment_id),
            recipe_id=UUID(recipe_id),
            user_id=UUID(user_id),
            text=text,
            image_urls=images,
        )
        await db["comments"].replace_one(
            {"_id": comment_id},
            {
                "_id": comment_id,
                "recipe_id": recipe_id,
                "user_id": user_id,
                "text": comment.text,
                "image_urls": comment.image_urls,
                "created_at": comment.created_at,
            },
            upsert=True,
        )

    return True


async def run_seed():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("MONGODB_DATABASE", "culinary_book")]
    seeded = await seed_database(db)
    await ensure_admin_account(db)
    client.close()
    return seeded


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(run_seed())
    print("Seeded database." if result else "Database already has data, skipped.")
