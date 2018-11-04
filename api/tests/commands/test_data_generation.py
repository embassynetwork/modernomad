from django.test import TransactionTestCase
from django.core.management import call_command


class DataGenerationTest(TransactionTestCase):

    def test_run_data_generation(self):
        call_command('generate_test_data')
