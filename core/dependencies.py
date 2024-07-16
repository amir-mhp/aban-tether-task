import json
from functools import wraps

import walrus
from nameko.extensions import DependencyProvider
from nameko.rpc import ServiceRpc


class MemoryStore(DependencyProvider):
    """Dependency provider for redis."""

    def __init__(self):
        self.client = None

    def setup(self):
        self.config = self.container.config['REDIS']

    def start(self):
        self.client = walrus.Database(**self.config)

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client


class Auth:
    memory_store = 'memory_store'

    def token_required(self, *outer_args, **outer_kwargs):
        token_type = 'Bearer'

        def arg_wrapper(func):
            @wraps(func)
            def decorator(svc, request, *args, **kwargs):
                auth_token = request.headers.get('Authorization')

                if not auth_token:
                    raise Exception("You need to set 'Authorization' header")

                try:
                    type, token = auth_token.split(' ')
                except ValueError:
                    raise Exception("'Authorization' header is not valid")

                if type != token_type:
                    raise Exception("'Authorization' header is not valid")

                memory_store = getattr(svc, Auth.memory_store)
                access_info = memory_store.get(token)
                if access_info:
                    access_info = json.loads(access_info)

                if not access_info or not access_info.get('user', None):
                    raise Exception("Invalid authorization token, You need to login again")

                if hasattr(request, 'access_info'):
                    request.access_info.update(access_info)
                else:
                    request.access_info = access_info

                return func(svc, request, *args, **kwargs)

            return decorator

        if outer_args and callable(outer_args[0]):
            return arg_wrapper(outer_args[0])

        return arg_wrapper
