from django.contrib.auth import get_user_model

from . import factory

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    # all users have a password hardcoded to 'password'
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_staff = factory.Faker('pybool')
    is_active = True
    is_superuser = False


class SuperUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = 'admin'
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = 'Root'
    last_name = 'Admin'
    email = factory.Faker('email')
    is_superuser = True
    is_active = True
    is_staff = True


class UserProfileFactory(factory.DjangoModelFactory):
    pass


class UserNote(factory.DjangoModelFactory):
    pass
