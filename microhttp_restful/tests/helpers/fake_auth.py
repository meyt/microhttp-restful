import functools
from nanohttp import context


class DummyIdentity:
    roles = list()


# Fake authorization decorator
def authorize(*roles):  # pragma: nocover

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context.identity = DummyIdentity()
            context.identity.roles = str(context.environ.get('fake_roles', '')).split(',')
            return func(*args, **kwargs)

        return wrapper

    if roles and callable(roles[0]):
        f = roles[0]
        return decorator(f)
    else:
        return decorator

