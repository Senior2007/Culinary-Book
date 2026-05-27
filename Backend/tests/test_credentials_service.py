# tests/test_credentials_service.py
import pytest
from uuid import UUID
from Application.Services.CredentialsServices.CredentialService import CredentialsService

@pytest.mark.asyncio
async def test_register_new_user(credentials_service, mock_user_repo):
    user_id = await credentials_service.register("test_user", "Password1", "test@example.com")
    assert isinstance(user_id, UUID)
    
    user = await mock_user_repo.get_by_id(user_id)
    assert user is not None
    assert user.credentials.login == "test_user"
    assert user.credentials.email == "test@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_login(credentials_service):
    await credentials_service.register("test_user", "Password1", "test@example.com")
    with pytest.raises(ValueError):
        await credentials_service.register("test_user", "Password2", "other@example.com")

@pytest.mark.asyncio
async def test_authenticate_success(credentials_service):
    user_id = await credentials_service.register("test_user", "Password1", "test@example.com")
    auth_id = await credentials_service.authenticate("test_user", "Password1")
    assert auth_id == user_id

@pytest.mark.asyncio
async def test_authenticate_wrong_password(credentials_service):
    await credentials_service.register("test_user", "Password1", "test@example.com")
    with pytest.raises(ValueError):
        await credentials_service.authenticate("test_user", "wrong")


@pytest.mark.asyncio
async def test_bo_user_with_login(credentials_service):
    await credentials_service.register("test_user", "Password1", "test@example.com")
    with pytest.raises(ValueError):
        await credentials_service.authenticate("wrong_user", "wrong")
