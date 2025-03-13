import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from shop.models import ProductModel, ProductCategoryModel, ProductStatusType
from accounts.models import CustomUser
from pathlib import Path
from django.core.files import File

BASE_DIR = Path(__file__).resolve().parent

class Command(BaseCommand):
    help = 'Generate fake products'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of products to create')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        fake = Faker(locale="fa_IR")
        
        # ایجاد یا گرفتن کاربر
        user, created = CustomUser.objects.get_or_create(
            email="create_products@example.com",
            defaults={'password': "CreateProducts7100865@"}
        )
        
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

        # دریافت دسته‌بندی‌های پدر
        parent_categories = ProductCategoryModel.objects.filter(parent__isnull=False)

        for _ in range(count):
            if parent_categories:  # اطمینان از وجود دسته‌بندی‌های پدر
                selected_category = random.choice(parent_categories)
            else:
                selected_category = None  # یا مدیریت حالت عدم وجود دسته‌بندی

            title = ' '.join([fake.word() for _ in range(1, 3)])
            slug = slugify(title, allow_unicode=True)
            selected_image = random.choice(image_list)
            image_obj = File(open(BASE_DIR / selected_image, "rb"), name=Path(selected_image).name)
            description = fake.paragraph(nb_sentences=10)
            brief_description = fake.paragraph(nb_sentences=1)
            stock = fake.random_int(min=0, max=10)

            # اطمینان از وجود انواع وضعیت محصول
            if ProductStatusType.choices:
                status = random.choice(ProductStatusType.choices)[0]
            else:
                status = 0  # یا هر وضعیت پیش‌فرض دیگر

            price = fake.random_int(min=10000, max=100000)
            discount_percent = fake.random_int(min=0, max=50)

            # ایجاد محصول
            ProductModel.objects.create(
                user=user,
                category=selected_category,  # اختصاص دسته‌بندی انتخاب‌شده
                title=title,
                slug=slug,
                image=image_obj,
                description=description,
                brief_description=brief_description,
                stock=stock,
                status=status,
                price=price,
                discount_percent=discount_percent,
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} fake products'))
