from faker import Faker
from fakers.providers import lorem
from fakers.providers import profile
from fakers.providers import address
from fakers.providers import python
from faker.providers import BaseProvider
import factory

factory.Faker.add_provider(python)
factory.Faker.add_provider(lorem)
factory.Faker.add_provider(profile)
factory.Faker.add_provider(address)


class Provider(BaseProvider):
    # Note that the class name _must_ be ``Provider``.
    def slug(self, provider):
        fake = Faker()
        value = getattr(fake, provider)()
        return value.replace(' ', '-')


factory.Faker.add_provider(Provider)

