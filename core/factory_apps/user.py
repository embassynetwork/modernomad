from django.contrib.auth import get_user_model

from . import factory

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_staff = factory.Faker('pybool')
    is_active = True
    is_superuser = False


class UserProfileFactory(factory.DjangoModelFactory):
    pass


class UserNote(factory.DjangoModelFactory):
    pass
