import pytest

from unittest.mock import MagicMock
from core.services.user import UserService
from core.repositories.user import UserRepository
from core.models.user import UserEntity
from core.utils.hashers import make_password


@pytest.fixture
def user_repo():
    return MagicMock(UserRepository)


@pytest.fixture
def memory_store():
    return MagicMock()


@pytest.fixture
def user_service(user_repo, memory_store):
    access_info = {}
    return UserService(access_info=access_info, user_repo=user_repo, memory_store=memory_store)


class TestUser:

    def test_create_user(self, user_service, user_repo):
        user_data = {
            'phone': '1234567890',
            'password': 'password123',
            'first_name': 'Amir',
            'last_name': 'Mhp'
        }

        user_repo.get_user_by_phone.return_value = None

        created_user = user_service.create_user(user_data)

        assert created_user.phone == user_data['phone']
        user_repo.create_user.assert_called_once()

    def test_create_user_phone_exists(self, user_service, user_repo):
        user_data = {
            'phone': '1234567890',
            'password': 'password123',
            'first_name': 'Amir',
            'last_name': 'Mhp'
        }

        user_repo.get_user_by_phone.return_value = True

        with pytest.raises(Exception, match="User with this phone already exists"):
            user_service.create_user(user_data)

    def test_authenticate_user(self, user_service, user_repo, memory_store):
        user_data = {
            'phone': '1234567890',
            'password': 'password123'
        }

        hashed_password = make_password(user_data['password'])
        user_entity = UserEntity(phone=user_data['phone'], password=hashed_password, first_name="Amir", last_name="Mhp")

        user_repo.get_user_by_phone.return_value = user_entity
        memory_store.set = MagicMock()

        response = user_service.authenticate(user_data)

        assert 'token' in response
        assert 'user' in response
        memory_store.set.assert_called_once()

    def test_authenticate_user_invalid_phone(self, user_service, user_repo):
        user_data = {
            'phone': '1234567890',
            'password': 'password123'
        }

        user_repo.get_user_by_phone.return_value = None

        with pytest.raises(Exception, match="Phone and password does not match"):
            user_service.authenticate(user_data)

    def test_authenticate_user_invalid_password(self, user_service, user_repo):
        user_data = {
            'phone': '1234567890',
            'password': 'password123'
        }

        hashed_password = make_password('wrong_password')
        user_entity = UserEntity(phone=user_data['phone'], password=hashed_password, first_name="Amir", last_name="Mhp")

        user_repo.get_user_by_phone.return_value = user_entity

        with pytest.raises(Exception, match="Phone and password does not match"):
            user_service.authenticate(user_data)
