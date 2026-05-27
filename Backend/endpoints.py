from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient
from Application.Services.CredentialsServices.CredentialService import CredentialsService
from Application.Services.UserServices.ReaderService import ReaderService
from Application.Services.UserServices.AuthorServices import AuthorServices
from Application.Services.RecipeBookServices.RecipeBookService import RecipeBookService
from Application.Services.RecipeServices.RecipeService import RecipeService
from Infrastructure.Repositories.MongoUserRepository import MongoUserRepository
from Infrastructure.Repositories.MongoRecipeRepository import MongoRecipeRepository
from Domain.Entities.Recipe.Recipe import Tag, Ingredient, Step
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from asyncio import gather
from Application.Services.RaitingService.RatingService import RatingService
from Infrastructure.Repositories.MongoRaitingRepository import MongoRaitingRepository
from Infrastructure.Repositories.MongoCommentRepository import MongoCommentRepository
from Application.Services.CommentServices.CommentService import CommentService
from typing import Optional, List
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    from seed import ensure_admin_account
    if os.getenv("SEED_ON_STARTUP", "true").lower() in ("1", "true", "yes"):
        from seed import seed_database
        seeded = await seed_database(db)
        if seeded:
            print("Database seeded with demo data.")
    admin_created = await ensure_admin_account(db)
    if admin_created:
        print("Admin account created.")
    yield

app = FastAPI(lifespan=lifespan)

# Добавленный CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup (override with MONGODB_URL if needed)
mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = mongo_client[os.getenv("MONGODB_DATABASE", "culinary_book")]

# Repositories
user_repo = MongoUserRepository(db)
recipe_repo = MongoRecipeRepository(db)
rating_repo = MongoRaitingRepository(db)
comment_repo = MongoCommentRepository(db)

# Services
credentials_service = CredentialsService(user_repo=user_repo)
reader_service = ReaderService(user_repo=user_repo, recipe_repo=recipe_repo, book_service=RecipeBookService())
author_service = AuthorServices(recipe_repo=recipe_repo)
rating_service = RatingService(repository=rating_repo)
recipe_service = RecipeService(recipe_repo=recipe_repo)
comment_service = CommentService(comment_repo=comment_repo, recipe_repo=recipe_repo)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate")

class RegisterRequest(BaseModel):
    login: str
    password: str
    email: str

class CommentRequest(BaseModel):
    text: str
    image_urls: List[str] = []

class CommentUpdateRequest(BaseModel):
    text: str
    image_urls: List[str] | None = None

class AuthenticateRequest(BaseModel):
    login: str
    password: str

class RecipeRequest(BaseModel):
    title: str
    cover_url: str | None = None

class IngredientRequest(BaseModel):
    name: str
    ingredient_id: UUID

class StepRequest(BaseModel):
    description: str

class TagRequest(BaseModel):
    name: str

class ImageRequest(BaseModel):
    image_url: str

@app.post("/register")
async def register_user(request: RegisterRequest):
    try:
        user_id = await credentials_service.register(
            request.login, request.password, request.email
        )
        await rating_service.add_rating_to_user(user_id, 0)
        token = credentials_service.generate_token(user_id)
        return {"user_id": str(user_id), "token": token, "is_admin": False, "is_banned": False}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/authenticate")
async def authenticate_user(request: AuthenticateRequest):
    try:
        user_id = await credentials_service.authenticate(request.login, request.password)
        user = await user_repo.get_by_id(user_id)
        token = credentials_service.generate_token(user_id)
        return {
            "user_id": str(user_id),
            "token": token,
            "is_admin": user.credentials.is_admin if user else False,
            "is_banned": user.credentials.is_banned if user else False,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        user_id = credentials_service.validate_token(token)
        return user_id
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_user_entity(current_user: UUID = Depends(get_current_user)):
    user = await user_repo.get_by_id(current_user)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_admin(current_user=Depends(get_current_user_entity)):
    if not current_user.credentials.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def is_admin_user(user_id: UUID) -> bool:
    user = await user_repo.get_by_id(user_id)
    return bool(user and user.credentials.is_admin)

async def ensure_user_not_banned(user_id: UUID):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.credentials.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")

async def can_modify_recipe(recipe_id: UUID, user_id: UUID) -> bool:
    return await is_admin_user(user_id) or await author_service.is_author(recipe_id, user_id)

@app.get("/me")
async def get_me(current_user=Depends(get_current_user_entity)):
    return {
        "user_id": str(current_user.credentials.id),
        "login": current_user.credentials.login,
        "email": current_user.credentials.email,
        "is_admin": current_user.credentials.is_admin,
        "is_banned": current_user.credentials.is_banned,
    }

@app.post("/recipes")
async def create_recipe(request: RecipeRequest, current_user: UUID = Depends(get_current_user)):
    try:
        recipe_id = await author_service.create_recipe(current_user, request.title, request.cover_url)
        return {"recipe_id": str(recipe_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/recipes/{recipe_id}")
async def create_recipe(request: RecipeRequest, recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    try:
        if not await can_modify_recipe(recipe_id, current_user):
            raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
        recipe_id = await author_service.save_recipe(request.title, recipe_id, request.cover_url)
        return {"recipe_id": str(recipe_id)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipes/{recipe_id}/ingredients")
async def add_ingredient(recipe_id: UUID, request: IngredientRequest, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    ingredient = Ingredient(name=request.name)
    await author_service.add_ingredient(recipe_id, ingredient)
    return {"status": "Ingredient added"}

@app.post("/recipes/{recipe_id}/steps")
async def add_step(recipe_id: UUID, request: StepRequest, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    step = Step(description=request.description, contents=[])
    await author_service.add_step(recipe_id, step)
    return {"status": "Step added"}

@app.post("/recipes/{recipe_id}/tags")
async def add_tag(recipe_id: UUID, request: TagRequest, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    tag = Tag(name=request.name)
    await author_service.add_tag(recipe_id, tag)
    return {"status": "Tag added"}

@app.post("/recipes/{recipe_id}/publish")
async def publish_recipe(recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    await ensure_user_not_banned(current_user)
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    recipe = await recipe_repo.get_by_id(recipe_id)
    await author_service.publish_recipe(recipe_id)
    if recipe:
        await rating_service.add_rating_to_user(recipe.author_id, 100)  # Add 100 points for publishing
    return {"status": "Recipe published"}

@app.post("/recipes/{recipe_id}/steps/{step_index}/images")
async def add_image_to_step(recipe_id: UUID, step_index: int, request: ImageRequest, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await author_service.add_image_to_step(recipe_id, step_index, request.image_url)
    return {"status": "Image added to step"}

@app.post("/recipe-book/{user_id}/add")
async def add_recipe_to_book(user_id: UUID, recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.add_recipe_to_book(user_id, recipe_id)
    recipe = await recipe_repo.get_by_id(recipe_id)
    if recipe:
        await rating_service.add_rating_to_user(recipe.author_id, 100)  # Add 100 points to the author
    return {"status": "Recipe added to book"}

@app.post("/recipe-book/{user_id}/remove")
async def remove_recipe_from_book(user_id: UUID, recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.remove_recipe_from_book(user_id, recipe_id)
    return {"status": "Recipe removed from book"}

@app.post("/recipe-book/{user_id}/steps/{recipe_id}/{step_index}/complete")
async def mark_step_as_completed(user_id: UUID, recipe_id: UUID, step_index: int, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.mark_step_as_completed(user_id, recipe_id, step_index)
    await rating_service.add_rating_to_user(current_user, 10)  # Add 100 points for completing a step
    return {"status": "Step marked as completed"}

@app.post("/recipe-book/{user_id}/steps/{recipe_id}/{step_index}/uncomplete")
async def unmark_step_as_completed(user_id: UUID, recipe_id: UUID, step_index: int, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.unmark_step_as_completed(user_id, recipe_id, step_index)
    await rating_service.delete_rating_from_user(current_user, 10)  # Subtract 100 points for unmarking a step
    return {"status": "Step unmarked as completed"}

@app.post("/recipe-book/{user_id}/ingredients/{recipe_id}/{ingredient_name}/missing")
async def mark_ingredient_as_missing(user_id: UUID, recipe_id: UUID, ingredient_name: str, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.mark_ingredient_as_missing(user_id, recipe_id, ingredient_name)
    return {"status": "Ingredient marked as missing"}

@app.post("/recipe-book/{user_id}/ingredients/{recipe_id}/{ingredient_name}/unmissing")
async def unmark_ingredient_as_missing(user_id: UUID, recipe_id: UUID, ingredient_name: str, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    await reader_service.unmark_ingredient_as_missing(user_id, recipe_id, ingredient_name)
    return {"status": "Ingredient unmarked as missing"}

@app.get("/recipe-book/{user_id}/missing-ingredients")
async def get_missing_ingredients(user_id: UUID, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    missing_ingredients = await reader_service.get_missing_ingredients(user_id)
    return {"missing_ingredients": [str(ingredient) for ingredient in missing_ingredients]}

@app.get("/recipes/search")
async def search_recipes(tags: Optional[str] = None, ingredients: list[str] = None, query: str = None):
    print(tags)
    tag_objects = [Tag(name=tags)] if tags else []
    ingredient_objects = [Ingredient(name=ingredient) for ingredient in ingredients] if ingredients else []
    recipes = await recipe_service.find_recipes(tag_objects, ingredient_objects, query)
    return {
        "recipes": [
            {
                "id": str(recipe.id),
                "title": recipe.title,
                "is_published": recipe.is_published,
                "cover_url": recipe.cover_url,
            }
            for recipe in recipes
        ]
    }

@app.get("/recipes/author/{author_id}")
async def get_user_recipes(author_id: UUID, current_user: UUID = Depends(get_current_user)):
    if author_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    recipes = await author_service.get_user_recipes(author_id)
    return {
        "recipes": [
            {
                "id": str(recipe.id),
                "title": recipe.title,
                "is_published": recipe.is_published,
            }
            for recipe in recipes
        ]
    }

@app.get("/ratings/{user_id}")
async def get_all_recipes(user_id: UUID, current_user: UUID = Depends(get_current_user)):
    rating = await rating_service.get_rating_by_id(user_id)
    return {"rating": rating}

@app.get("/ratings")
async def get_sorted_ratings():
    ratings = await rating_repo.get_all_ratings()
    sorted_ratings = sorted(ratings, key=lambda x: x["rating"], reverse=True)
    result = []
    for r in sorted_ratings:
        user = await user_repo.get_by_id(UUID(r["_id"]) if isinstance(r["_id"], str) else r["_id"])
        if user:
            result.append({
                "user_id": str(user.credentials.id),
                "login": user.credentials.login,
                "email": user.credentials.email,
                "rating": r["rating"],
            })
    return {"ratings": result}

@app.get("/recipes")
async def get_all_recipes():
    recipes = await author_service.get_all_recipes()
    return {
        "recipes": [
            {
                "id": str(recipe.id),
                "title": recipe.title,
                "is_published": recipe.is_published,
                "cover_url": recipe.cover_url,
            }
            for recipe in recipes
        ]
    }

@app.get("/ingredients")
async def get_all_ingredients():
    ingredients = await author_service.get_all_ingredients()
    return {"ingredients": [ingredient.name for ingredient in ingredients]}

@app.get("/tags")
async def get_all_tags():
    tags = await author_service.get_all_tags()
    return {"tags": [tag.name for tag in tags]}

@app.get("/recipe-book/{user_id}/recipes")
async def get_recipes_from_book(user_id: UUID, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    recipes = await reader_service.get_all_book_entries(user_id)

    detailed_recipes = await gather(*[
        recipe_repo.get_by_id(recipe.recipe_id) for recipe in recipes
    ])

    return {
        "recipes": [
            {"id": str(r.id), "title": r.title} for r in detailed_recipes if r is not None
        ]
    }

@app.get("/recipe-book/{user_id}/recipes/{recipe_id}/details")
async def get_recipe_details(user_id: UUID, recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    book_entry = (await reader_service.user_repo.get_by_id(user_id)).recipe_book.entries[recipe_id]
    if not book_entry:
        raise HTTPException(status_code=404, detail="Recipe not found in user's book")
    
    return {
        "missing_ingredients": [str(ingredient_id) for ingredient_id in book_entry.missing_ingredients],
        "completed_steps": book_entry.completed_steps
    }

@app.delete("/recipes/{recipe_id}/tags/{tag_name}")
async def remove_tag(recipe_id: UUID, tag_name: str, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.remove_tag(recipe_id, tag_name)
    return {"status": "Tag removed"}

@app.delete("/recipes/{recipe_id}/steps/{step_index}")
async def remove_step(recipe_id: UUID, step_index: int, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.remove_step(recipe_id, step_index)
    return {"status": "Step removed"}

@app.delete("/recipes/{recipe_id}/steps/{step_index}/images/{image_index}")
async def remove_step_image(recipe_id: UUID, step_index: int, image_index: int, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.remove_image_from_step(recipe_id, step_index, image_index)
    return {"status": "Step image removed"}

@app.delete("/recipes/{recipe_id}/ingredients/{ingredient_name}")
async def remove_ingredient(recipe_id: UUID, ingredient_name: str, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.remove_ingredient(recipe_id, ingredient_name)
    return {"status": "Ingredient removed"}

@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: UUID, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can delete the recipe")
    await comment_repo.delete_by_recipe(recipe_id)
    await recipe_repo.delete_recipe(recipe_id)
    return {"status": "Recipe deleted"}

@app.put("/recipes/{recipe_id}/steps/{step_index}")
async def update_step(recipe_id: UUID, step_index: int, description: str, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.update_step(recipe_id, step_index, description)
    return {"status": "Step updated"}

@app.put("/recipes/{recipe_id}/steps/{step_index}/description")
async def update_step_description(recipe_id: UUID, step_index: int, description: str, current_user: UUID = Depends(get_current_user)):
    if not await can_modify_recipe(recipe_id, current_user):
        raise HTTPException(status_code=403, detail="Only recipe author or admin can modify content")
    await recipe_service.update_step_description(recipe_id, step_index, description)
    return {"status": "Step description updated"}

@app.get("/recipes/{recipe_id}")
async def get_recipe_by_id(recipe_id: UUID):
    recipe = await author_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {
        "id": str(recipe.id),
        "title": recipe.title,
        "ingredients": [{"name": ing.name} for ing in recipe.ingredients],
        "steps": [
            {
                "description": step.description,
                "contents": [{"url": c.url} for c in step.contents],
            }
            for step in recipe.steps
        ],
        "tags": [tag.name for tag in recipe.tags],
        "is_published": recipe.is_published,
        "author_id": str(recipe.author_id)
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: UUID):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rating = await rating_service.get_rating_by_id(user_id)
    return {
        "user_id": str(user.credentials.id),
        "login": user.credentials.login,
        "email": user.credentials.email,
        "rating": rating,
        "is_admin": user.credentials.is_admin,
        "is_banned": user.credentials.is_banned,
    }


@app.get("/recipes/{recipe_id}/comments")
async def list_comments(recipe_id: UUID):
    comments = await comment_service.get_comments(recipe_id)
    result = []
    for comment in comments:
        author = await user_repo.get_by_id(comment.user_id)
        result.append({
            "id": str(comment.id),
            "text": comment.text,
            "image_urls": comment.image_urls,
            "created_at": comment.created_at,
            "user_id": str(comment.user_id),
            "author_login": author.credentials.login if author else "unknown",
            "author_email": author.credentials.email if author else "",
        })
    return {"comments": result}


@app.post("/recipes/{recipe_id}/comments")
async def create_comment(
    recipe_id: UUID,
    request: CommentRequest,
    current_user: UUID = Depends(get_current_user),
):
    try:
        await ensure_user_not_banned(current_user)
        comment = await comment_service.add_comment(
            recipe_id, current_user, request.text, request.image_urls
        )
        return {"comment_id": str(comment.id), "status": "Comment added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: UUID, current_user: UUID = Depends(get_current_user)):
    try:
        comment = await comment_repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        if comment.user_id != current_user and not await is_admin_user(current_user):
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        await comment_repo.delete(comment_id)
        return {"status": "Comment deleted"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/comments/{comment_id}")
async def update_comment(
    comment_id: UUID,
    request: CommentUpdateRequest,
    current_user=Depends(require_admin),
):
    comment = await comment_repo.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Comment text is required")

    comment.text = text
    if request.image_urls is not None:
        comment.image_urls = [
            url.strip() for url in request.image_urls if url and url.strip()
        ]
    await comment_repo.save(comment)
    return {"status": "Comment updated"}


@app.get("/admin/users")
async def admin_list_users(current_user=Depends(require_admin)):
    users = await user_repo.get_all()
    return {
        "users": [
            {
                "user_id": str(user.credentials.id),
                "login": user.credentials.login,
                "email": user.credentials.email,
                "is_admin": user.credentials.is_admin,
                "is_banned": user.credentials.is_banned,
            }
            for user in users
        ]
    }


@app.post("/admin/users/{user_id}/ban")
async def admin_ban_user(user_id: UUID, current_user=Depends(require_admin)):
    if user_id == current_user.credentials.id:
        raise HTTPException(status_code=400, detail="Admin cannot ban themselves")
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.credentials.is_admin:
        raise HTTPException(status_code=400, detail="Cannot ban another admin")
    user.credentials.is_banned = True
    await user_repo.save(user)
    return {"status": "User banned"}


@app.post("/admin/users/{user_id}/unban")
async def admin_unban_user(user_id: UUID, current_user=Depends(require_admin)):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.credentials.is_banned = False
    await user_repo.save(user)
    return {"status": "User unbanned"}


@app.get("/admin/comments")
async def admin_list_comments(current_user=Depends(require_admin)):
    comments = await comment_repo.get_all()
    result = []
    for comment in comments:
        author = await user_repo.get_by_id(comment.user_id)
        recipe = await recipe_repo.get_by_id(comment.recipe_id)
        result.append({
            "id": str(comment.id),
            "recipe_id": str(comment.recipe_id),
            "recipe_title": recipe.title if recipe else "unknown",
            "text": comment.text,
            "image_urls": comment.image_urls,
            "created_at": comment.created_at,
            "user_id": str(comment.user_id),
            "author_login": author.credentials.login if author else "unknown",
            "author_email": author.credentials.email if author else "",
        })
    return {"comments": result}


_frontend_dir = Path(__file__).resolve().parent.parent / "Frontend"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
