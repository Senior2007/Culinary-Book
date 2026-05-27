import pytest
from tests.mocks import MockRecipeRepository, MockUserRepository
from Application.Services.CredentialsServices.CredentialService import CredentialsService
from Application.Services.RecipeServices.RecipeService import RecipeService
from Application.Services.UserServices.ReaderService import ReaderService
from Application.Services.RecipeBookServices.RecipeBookService import RecipeBookService

@pytest.fixture
def mock_recipe_repo():
    return MockRecipeRepository()

@pytest.fixture
def mock_user_repo():
    return MockUserRepository()

@pytest.fixture
def book_service():
    return RecipeBookService()

@pytest.fixture
def credentials_service(mock_user_repo):
    return CredentialsService(mock_user_repo)

@pytest.fixture
def recipe_service(mock_recipe_repo):
    return RecipeService(mock_recipe_repo)

@pytest.fixture
def reader_service(mock_user_repo, mock_recipe_repo, book_service):
    return ReaderService(mock_user_repo, mock_recipe_repo, book_service)