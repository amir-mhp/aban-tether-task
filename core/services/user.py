import datetime
import json
import uuid

from nameko import config

from core import response_schemas
from core.entities.user import UserEntity
from core.hashers import make_password, check_password
from core.repositories.user import UserRepository


class UserService:

    def __init__(
            self,
            access_info,
            user_repo: UserRepository,
            memory_store,
    ):
        self.access_info = access_info
        self.user_repo = user_repo
        self.memory_store = memory_store

    def create_user(self, data):
        user_phone_exist = self.user_repo.get_user_by_phone(data['phone'])

        if user_phone_exist:
            raise Exception("User with this phone already exists")

        password = data.pop('password')

        user_entity = UserEntity(
            password=make_password(password),
            **data
        )

        self.user_repo.create_user(
            entity=user_entity
        )

        return user_entity

    def authenticate(self, data):
        phone = data['phone']
        password = data['password']

        user_exist = self.user_repo.get_user_by_phone(phone)

        if not user_exist:
            raise Exception("Phone and password does not match")

        if not user_exist or not check_password(password, user_exist.password):
            raise Exception("Phone and password does not match")

        uuid_token = uuid.uuid4().hex

        access_info = {
            'user': response_schemas.UserSchema().dump(user_exist),
            'token': uuid_token
        }

        ttl = datetime.timedelta(
            days=config.get('SESSION_LIFETIME_DAYS', 1)
        ).total_seconds()

        self.memory_store.set(uuid_token, json.dumps(access_info), ex=int(ttl))

        return access_info
