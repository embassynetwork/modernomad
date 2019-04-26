from . import factory
import factory.fuzzy
from bank.models import Currency
from bank.models import Account
from .user import UserFactory


class DRFTCurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Currency
        # Currencies are created in migrations, so use that if it exists
        django_get_or_create = ('name',)
    name = "DRFT"
    symbol = "Ɖ"


class USDCurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Currency
        # Currencies are created in migrations, so use that if it exists
        django_get_or_create = ('name',)
    name = "USD"
    symbol = "$"


class USDAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = Account
    currency = factory.SubFactory(USDCurrencyFactory)
    # JKS this is a hack. Just makes the primary superuser the account
    # owner/admin.
    name = factory.fuzzy.FuzzyText(length=10)

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            for user in extracted:
                self.admins.add(user)
        else:
            self.admins.add(UserFactory())

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            for user in extracted:
                self.owners.add(user)
        else:
            self.owners.add(UserFactory())


class DRFTAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = Account
    currency = factory.SubFactory(DRFTCurrencyFactory)
    # JKS this is a hack. Just makes the primary superuser the account
    # owner/admin.
    name = factory.fuzzy.FuzzyText(length=10)

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            for user in extracted:
                self.admins.add(user)
        else:
            self.admins.add(UserFactory())

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            for user in extracted:
                self.owners.add(user)
        else:
            self.owners.add(UserFactory())


class UserPrimaryAccountFactory(factory.DjangoModelFactory):
    pass


class HouseAccountFactory(factory.DjangoModelFactory):
    pass


class UseTransactionFactory(factory.DjangoModelFactory):
    pass
