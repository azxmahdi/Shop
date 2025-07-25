from django.core.management.base import BaseCommand

from shop.models import ProductCategoryModel


class Command(BaseCommand):
    help = "ایجاد دسته‌های پایه با ساختار سلسله‌مراتبی"

    def handle(self, *args, **kwargs):
        categories_data = [
            {
                "title": "وسایل دیجیتال",
                "slug": "digital-devices",
                "subcategories": [
                    {"title": "تلفن‌های همراه", "slug": "mobile-phones"},
                    {
                        "title": "لوازم جانبی",
                        "slug": "electronics-accessories",
                    },
                    {
                        "title": "تلویزیون و سینما خانگی",
                        "slug": "home-theater-tv",
                    },
                    {"title": "لپ‌تاپ و کامپیوتر", "slug": "laptops-computers"},
                    {"title": "دستگاه‌های بازی", "slug": "gaming-consoles"},
                ],
            },
            {
                "title": "مد و پوشاک",
                "slug": "fashion-clothing",
                "subcategories": [
                    {"title": "لباس زنانه", "slug": "womens-clothing"},
                    {"title": "لباس مردانه", "slug": "mens-clothing"},
                    {"title": "کفش", "slug": "shoes"},
                    {"title": "اکسسوری", "slug": "fashion-accessories"},
                    {"title": "کیف و چمدان", "slug": "bags-luggage"},
                ],
            },
            {
                "title": "خانه و آشپزخانه",
                "slug": "home-kitchen",
                "subcategories": [
                    {"title": "وسایل دکوری", "slug": "decorative-items"},
                    {"title": "لوازم آشپزخانه", "slug": "kitchen-appliances"},
                    {
                        "title": "مبلمان و دکوراسیون",
                        "slug": "furniture-decoration",
                    },
                    {"title": "تجهیزات نظافت", "slug": "cleaning-equipment"},
                    {"title": "روشنایی", "slug": "lighting"},
                ],
            },
            {
                "title": "ورزش و تناسب اندام",
                "slug": "sports-fitness",
                "subcategories": [
                    {"title": "تجهیزات ورزشی", "slug": "sports-equipment"},
                    {"title": "لباس ورزشی", "slug": "sportswear"},
                    {"title": "مکمل‌های ورزشی", "slug": "sports-supplements"},
                    {
                        "title": "لوازم بدن‌سازی",
                        "slug": "bodybuilding-equipment",
                    },
                    {"title": "ورزش در فضای باز", "slug": "outdoor-sports"},
                ],
            },
            {
                "title": "سلامتی و زیبایی",
                "slug": "health-beauty",
                "subcategories": [
                    {"title": "مکمل‌های غذایی", "slug": "dietary-supplements"},
                    {"title": "مراقبت از پوست", "slug": "skincare"},
                    {"title": "آرایش", "slug": "makeup"},
                    {"title": "لوازم آرایشی", "slug": "cosmetics"},
                    {"title": "لوازم پزشکی", "slug": "medical-supplies"},
                ],
            },
            {
                "title": "کودک و نوزاد",
                "slug": "baby-child",
                "subcategories": [
                    {"title": "لباس کودک", "slug": "childrens-clothing"},
                    {"title": "اسباب بازی", "slug": "toys"},
                    {"title": "لوازم نوزاد", "slug": "baby-essentials"},
                    {"title": "کتاب و آموزش", "slug": "books-education"},
                    {"title": "وسایل سیسمونی", "slug": "maternity-items"},
                ],
            },
            {
                "title": "کتاب و سرگرمی",
                "slug": "books-entertainment",
                "subcategories": [
                    {"title": "کتاب‌های fiction", "slug": "fiction-books"},
                    {
                        "title": "کتاب‌های غیر داستانی",
                        "slug": "non-fiction-books",
                    },
                    {"title": "بازی‌های رومیزی", "slug": "board-games"},
                    {"title": "لوازم هنری", "slug": "art-supplies"},
                    {"title": "فیلم و موسیقی", "slug": "movies-music"},
                ],
            },
            {
                "title": "باغ و حیاط",
                "slug": "garden-yard",
                "subcategories": [
                    {"title": "لوازم باغبانی", "slug": "gardening-tools"},
                    {"title": "گیاهان و گل‌ها", "slug": "plants-flowers"},
                    {"title": "تجهیزات فضای باز", "slug": "outdoor-equipment"},
                    {"title": "دکوراسیون حیاط", "slug": "yard-decor"},
                    {
                        "title": "تجهیزات آبیاری",
                        "slug": "irrigation-equipment",
                    },
                ],
            },
        ]

        for main_cat in categories_data:
            parent, created = ProductCategoryModel.objects.get_or_create(
                title=main_cat["title"],
                slug=main_cat["slug"],
                defaults={"parent": None},
            )
            for subcat in main_cat["subcategories"]:
                subcategory, created = (
                    ProductCategoryModel.objects.get_or_create(
                        title=subcat["title"],
                        slug=subcat["slug"],
                        defaults={"parent": parent},
                    )
                )
        self.stdout.write(
            self.style.SUCCESS(
                "All parent categories and subcategories were successfully created."
            )
        )
