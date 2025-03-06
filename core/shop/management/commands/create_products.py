import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from shop.models import ProductModel, ProductCategoryModel,ProductStatusType
from accounts.models import CustomUser, UserType
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
        try: 
            user = CustomUser.objects.get(email="create_products@example.com")
        except CustomUser.DoesNotExist:

            user = CustomUser.objects.create_superuser(
                email="create_products@example.com",
                password="CreateProducts7100865@",  
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

        categories = ProductCategoryModel.objects.all()
        for _ in range(count): 
            user = user  
            num_categories = random.randint(1, 4)
            selected_categoreis = random.sample(list(categories), num_categories)
            title = ' '.join([fake.word() for _ in range(1,3)])
            slug = slugify(title,allow_unicode=True)
            selected_image = random.choice(image_list)
            image_obj = File(file=open(BASE_DIR / selected_image,"rb"),name=Path(selected_image).name)
            description = fake.paragraph(nb_sentences=10)
            brief_description= fake.paragraph(nb_sentences=1)
            stock = fake.random_int(min=0, max=10)
            status = random.choice(ProductStatusType.choices)[0]
            price = fake.random_int(min=10000, max=100000)
            discount_percent = fake.random_int(min=0, max=50)

            product = ProductModel.objects.create(
                user=user,
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
            product.category.set(selected_categoreis)
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} fake products'))
