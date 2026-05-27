from uuid import UUID

from Application.Interfaces.ICommentRepository import ICommentRepository
from Application.Interfaces.IRecipeRepository import IRecipeRepository
from Domain.Entities.Recipe.Comment import Comment


class CommentService:
    def __init__(
        self,
        comment_repo: ICommentRepository,
        recipe_repo: IRecipeRepository,
    ):
        self.comment_repo = comment_repo
        self.recipe_repo = recipe_repo

    async def add_comment(
        self,
        recipe_id: UUID,
        user_id: UUID,
        text: str,
        image_urls: list[str],
    ) -> Comment:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise ValueError("Recipe not found")
        if not recipe.is_published:
            raise ValueError("Comments are only allowed on published recipes")

        text = text.strip()
        if not text:
            raise ValueError("Comment text is required")

        image_urls = [url.strip() for url in image_urls if url and url.strip()]

        comment = Comment(
            recipe_id=recipe_id,
            user_id=user_id,
            text=text,
            image_urls=image_urls,
        )
        await self.comment_repo.save(comment)
        return comment

    async def get_comments(self, recipe_id: UUID) -> list[Comment]:
        return await self.comment_repo.get_by_recipe(recipe_id)

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found")
        if comment.user_id != user_id:
            raise ValueError("You can only delete your own comments")
        await self.comment_repo.delete(comment_id)
