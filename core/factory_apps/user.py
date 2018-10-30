from django.contrib.auth import get_user_model

from . import factory

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.faker('name')
    first_name = factory.faker('name')
    last_name = factory.faker('lastname')
    email = factory.faker('email')
    is_staff = factory.faker('pyboolean')
    is_active = True
    is_superuser = False


class UserProfileFactory(factory.DjangoModelFactory):
    pass


class UserNote(factory.DjangoModelFactory):
    pass
