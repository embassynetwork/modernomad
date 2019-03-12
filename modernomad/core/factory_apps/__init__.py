from faker import Faker
from faker.providers import lorem
from faker.providers import profile
from faker.providers import address
from faker.providers import python
from faker.providers import date_time
from faker.providers import misc
from faker.providers import BaseProvider
import factory

factory.Faker.add_provider(misc)
factory.Faker.add_provider(date_time)
factory.Faker.add_provider(python)
factory.Faker.add_provider(lorem)
factory.Faker.add_provider(profile)
factory.Faker.add_provider(address)


class Provider(BaseProvider):
    # Note that the class name _must_ be ``Provider``.
    def slug(self, name):
        fake = Faker()
        value = getattr(fake, name)()
        return value.replace(' ', '-')


factory.Faker.add_provider(Provider)

