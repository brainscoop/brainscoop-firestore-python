import random
from faker import Faker
from faker_schema.faker_schema import FakerSchema
from faker_schema.schema_loader import load_json_from_file
from faker.providers import BaseProvider


class BornProvider(BaseProvider):
    def born(self):
        return str(random.randint(1950, 2000))


def generate(schema):
    fake = Faker()
    fake.add_provider(BornProvider)
    faker = FakerSchema(faker=fake)
    return faker.generate_fake(load_json_from_file(schema))
