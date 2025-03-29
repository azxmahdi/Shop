import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from random import randint, uniform
from faker import Faker
from django.core.files import File
from pathlib import Path

from shop.models import ProductCategoryModel, ProductModel, ProductFeature


BASE_DIR = Path(__file__).resolve().parent
fake = Faker('fa_IR')
User = get_user_model()

class Command(BaseCommand):
    help = 'ایجاد محصولات در تمام زیردسته‌ها با تعداد مشخص'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='تعداد محصول برای هر زیردسته')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        count = kwargs['count']
        user, created = User.objects.get_or_create(
            email="create_products@example.com",
            defaults={'password': "CreateProducts123@"}
        )
        subcategories = ProductCategoryModel.objects.exclude(parent__isnull=True)
        image_list = [
            "./img/img1.jpg",
            "./img/img2.jpg",
            "./img/img3.jpg",
            "./img/img4.jpg",
            "./img/img5.jpg",
            "./img/img6.jpg",
            "./img/img7.jpg",
            "./img/img8.jpg",
        ]
        for category in subcategories:
            
            for _ in range(count):
                title = f"{fake.word()} {category.title}"
                slug = slugify(title, allow_unicode=True)
                while ProductModel.objects.filter(slug=slug).exists():
                    slug += f"-{randint(1, 100)}"
                selected_image = random.choice(image_list)

                image_obj = File(open(BASE_DIR / selected_image, "rb"), name=Path(selected_image).name)

                product = ProductModel.objects.create(
                    user=user,
                    category=category,
                    title=title,
                    slug=slug,
                    image=image_obj,
                    price=randint(100000, 5000000),
                    stock=randint(0, 100),
                    status=1,
                    discount_percent=randint(0, 30)
                )

                self.assign_features(product)
                
        self.stdout.write(self.style.SUCCESS(f"{count} products were created for each category."))

    def assign_features(self, product):
        features = product.category.get_all_features()
        value_generators = {
            'ابعاد': lambda: f"{randint(100, 200)}x{randint(50, 150)} سانتیمتر",
            'وزن': lambda: f"{uniform(0.5, 5.0):.1f} کیلوگرم",
            'دوز': lambda: f"{randint(500, 2000)} میلیگرم",
            'سال چاپ': lambda: str(randint(1380, 1400)),
            'نیاز آبی': lambda: f"روزانه {randint(1, 3)} بار"
        }

        for feature in features:
            if feature.options.exists():
                option = feature.options.order_by('?').first()
                ProductFeature.objects.create(
                    product=product,
                    feature=feature,
                    option=option
                )
            else:
                generator = value_generators.get(
                    feature.name,
                    lambda: fake.word()
                )
                ProductFeature.objects.create(
                    product=product,
                    feature=feature,
                    value=generator()
                )
