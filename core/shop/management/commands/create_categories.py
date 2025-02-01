import random
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import ProductCategoryModel

class Command(BaseCommand):
    help = 'Create random product categories with Persian titles'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of categories to create')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        faker = Faker('fa_IR') 

        for _ in range(count):
            title = faker.word()  
            slug = title  


            category = ProductCategoryModel.objects.create(
                title=title,
                slug=slug
            )
            self.stdout.write(self.style.SUCCESS(f'Created category: {category.title}'))
