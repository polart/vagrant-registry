import random

import faker
from django.core.management.base import BaseCommand

from apps.boxes.models import Box
from apps.factories import UserFactory, StaffFactory, BoxFactory, BoxVersionFactory, PROVIDERS, BoxProviderFactory

STANDARD_USERS_COUNT = 23
STAFF_USERS_COUNT = 2
BOXES_COUNT_WEIGHTED = [0] * 2 + [1] * 10 + [2] * 12 + [3] * 9 + [4] * 3 + [5] * 2 + [12] * 1 + [14] * 1
BOXES_VISIBILITY_WEIGHTED = [Box.PRIVATE] * 10 + [Box.PUBLIC] * 2


class Command(BaseCommand):
    help = 'Creates fake users and boxes'

    def _create_boxes(self, owner):
        fake = faker.Faker()
        for i in range(random.choice(BOXES_COUNT_WEIGHTED)):
            box = BoxFactory(
                owner=owner,
                visibility=random.choice(BOXES_VISIBILITY_WEIGHTED),
            )
            for j in range(random.choice(BOXES_COUNT_WEIGHTED)):
                box_version = BoxVersionFactory(box=box)
                providers = random.sample(
                    PROVIDERS,
                    random.randint(0, len(PROVIDERS) - 1)
                )
                for provider in providers:
                    BoxProviderFactory(
                        file__data=fake.binary(random.randint(10, 1000)),
                        version=box_version,
                        provider=provider,
                    )

    def handle(self, *args, **options):
        for i in range(STANDARD_USERS_COUNT):
            self._create_boxes(UserFactory())

        for i in range(STAFF_USERS_COUNT):
            self._create_boxes(StaffFactory())

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created fake users and boxes'
            )
        )
