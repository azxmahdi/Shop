import random
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import ProductModel, ProductCategoryModel  
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from pathlib import Path
from django.core.files import File
 
BASE_DIR = Path(__file__).resolve().parent

User = get_user_model()

class Command(BaseCommand):
    help = 'Create fake products'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of products to create')

    def handle(self, *args, **options):
        fake = Faker('fa_IR')  
        count = options['count']

        categories = ProductCategoryModel.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.ERROR('No categories available. Please create some categories first.'))
            return

        # List of fake image URLs
        fake_image_urls = [
            './img/img1.jpg',
            './img/img2.jpg',
            './img/img3.jpg',
            './img/img4.jpg',
        ]

        for _ in range(count):
            title = fake.sentence(nb_words=3)
            slug = slugify(title,allow_unicode=True)
            category = random.choice(categories)  
            user = User.objects.get(id=1)
            selected_image = random.choice(fake_image_urls)
            image_obj = File(file=open(BASE_DIR / selected_image,"rb"),name=Path(selected_image).name)




            product = ProductModel.objects.create(
                user=user,
                title=title,
                slug=slug,
                description=fake.text(),
                brief_description=fake.text(),
                stock=random.randint(0, 100),
                status=random.choice([1, 2]),  
                price=random.randint(1000, 100000),
                discount_percent=random.randint(0, 50),
                avg_rate=random.uniform(1.0, 5.0),
                image=image_obj,  
            )

            product.category.add(category) 

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} products.'))
