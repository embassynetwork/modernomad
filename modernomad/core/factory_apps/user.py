from django.contrib.auth import get_user_model
from modernomad.core.models import UserProfile

from . import factory

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    # all users have a password hardcoded to 'password'
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_staff = False
    is_active = True
    is_superuser = False

    @factory.post_generation
    def create_profile(self, create, extracted, **kwargs):
        if not UserProfile.objects.filter(user=self).exists():
            UserProfileFactory(user=self)


class SuperUserFactory(UserFactory):
    username = 'admin'
    first_name = 'Root'
    last_name = 'Admin'
    is_superuser = True
    is_staff = True


class UserProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserProfile


class UserNote(factory.DjangoModelFactory):
    pass
