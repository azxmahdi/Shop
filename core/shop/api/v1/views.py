from django.core.cache import cache
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    Min,
    OuterRef,
    Prefetch,
    Q,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from review.api.v1.serializers import ReviewSerializer
from review.models import ReviewModel, ReviewStatusType
from shop.models import (
    CategoryFeature,
    ProductCategoryModel,
    ProductFeature,
    ProductModel,
    ProductStatusType,
    WishlistProductModel,
)

from .filters import CategoryFeatureFilter
from .pagination import ProductGridPagination
from .serializers import (
    AddOrRemoveWishlistSerializer,
    CategoryFeatureSerializer,
    CategoryTreeSerializer,
    MinPriceSerializer,
    PopularProductSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryFeatureAPI(ListAPIView):
    permission_classes = [AllowAny]
    queryset = CategoryFeature.objects.all()
    serializer_class = CategoryFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFeatureFilter


class ProductGridAPI(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    pagination_class = ProductGridPagination

    def get_queryset(self):
        queryset = (
            ProductModel.objects.filter(status=ProductStatusType.publish.value)
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "features",
                    queryset=ProductFeature.objects.select_related(
                        "feature", "option"
                    ),
                )
            )
        )
        queryset = self.apply_filters(queryset)

        wishlist_subquery = WishlistProductModel.objects.filter(
            product_id=OuterRef("pk"),
            user_id=(
                self.request.user.id
                if self.request.user.is_authenticated
                else None
            ),
        )

        queryset = queryset.annotate(
            is_wish=Exists(wishlist_subquery, output_field=BooleanField())
        )

        return queryset

    def apply_filters(self, queryset):
        if category_id := self.request.query_params.get("category_id"):
            category = ProductCategoryModel.objects.filter(
                id=category_id
            ).first()
            if category:
                if category.parent is None:
                    queryset = queryset.filter(
                        category__in=category.get_all_subcategories()
                    )
                else:
                    queryset = queryset.filter(category=category)

        if q := self.request.query_params.get("q"):
            queryset = queryset.filter(title__icontains=q)

        if min_price := self.request.query_params.get("min_price"):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.request.query_params.get("max_price"):
            queryset = queryset.filter(price__lte=max_price)

        for key, values in self.request.query_params.lists():
            if key.startswith("feature_"):
                feature_id = key.split("_")[1]
                values = [v for v in values if v.strip()]

                if not values:
                    continue

                subquery = ProductFeature.objects.filter(
                    product_id=OuterRef("id"), feature_id=feature_id
                ).filter(Q(option__value__in=values) | Q(value__in=values))

                queryset = queryset.annotate(
                    **{f"has_feature_{feature_id}": Exists(subquery)}
                ).filter(**{f"has_feature_{feature_id}": True})

        if order_by := self.request.query_params.get("order_by"):
            queryset = queryset.order_by(order_by)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProductDetailAPI(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value
    )
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()

        wishlist_subquery = WishlistProductModel.objects.filter(
            product_id=OuterRef("pk"),
            user_id=(
                self.request.user.id
                if self.request.user.is_authenticated
                else None
            ),
        )

        queryset = queryset.annotate(
            is_wish=Exists(wishlist_subquery, output_field=BooleanField())
        )

        return queryset

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        reviews = ReviewModel.objects.filter(
            product=self.get_object(), status=ReviewStatusType.accepted.value
        )
        response.data["reviews"] = ReviewSerializer(reviews, many=True).data

        total_reviews = reviews.count()
        star_counts = reviews.aggregate(
            **{
                f"star{star}": Count("pk", filter=Q(rate=star))
                for star in range(1, 6)
            }
        )
        response.data["star_counts"] = [
            (
                star,
                star_counts[f"star{star}"],
                (
                    round((star_counts[f"star{star}"] / total_reviews * 100))
                    if total_reviews
                    else 0
                ),
            )
            for star in reversed(range(1, 6))
        ]
        recommend_count = reviews.filter(rate__gte=4).count()
        response.data["recommend_percentage"] = (
            round((recommend_count / total_reviews) * 100)
            if total_reviews
            else 0
        )

        return response


class AddOrRemoveWishlistAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddOrRemoveWishlistSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data["product_id"]
            try:
                wishlist_item = WishlistProductModel.objects.get(
                    user=request.user, product__id=product_id
                )
                wishlist_item.delete()
                message = "محصول از لیست علایق حذف شد"
                return Response(
                    {
                        "status": "success",
                        "message": message,
                        "operation": "delete",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except WishlistProductModel.DoesNotExist:
                WishlistProductModel.objects.create(
                    user=request.user, product_id=product_id
                )
                message = "محصول به لیست علایق اضافه شد"
                return Response(
                    {
                        "status": "success",
                        "message": message,
                        "operation": "create",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        return Response(
            {
                "status": "failed",
                "errors": serializer.errors,
                "operation": "create",
            }
        )


class CategoriesSidebarAPI(APIView):
    def get(self, request):
        category_tree = cache.get("category_tree_data")
        if not category_tree:
            root_categories = ProductCategoryModel.objects.filter(
                parent__isnull=True
            ).prefetch_related("subcategories")

            serializer = CategoryTreeSerializer(
                root_categories, many=True, context={"request": request}
            )
            category_tree = serializer.data
            cache.set("category_tree_data", category_tree, 60 * 60 * 24 * 7)

        min_prices = cache.get("min_prices_data")
        if not min_prices:
            min_prices = self.get_min_prices()
            cache.set("min_prices_data", min_prices, 60 * 60 * 24 * 7)

        popular_products = self.get_popular_products(request)

        return Response(
            {
                "category_tree": category_tree,
                "min_prices": min_prices,
                "popular_products": popular_products,
            }
        )

    def get_min_prices(self):
        categories = ProductCategoryModel.objects.filter(
            slug__in=[
                "mobile-phones",
                "mens-clothing",
                "womens-clothing",
                "cosmetics",
            ]
        )

        min_prices = []
        for category in categories:
            min_price = self.get_category_min_price(category)

            min_prices.append(
                {
                    "category_id": category.id,
                    "min_price": min_price,
                    "category_slug": category.slug,
                    "category_title": category.title,
                }
            )

        return MinPriceSerializer(min_prices, many=True).data

    def get_category_min_price(self, category):
        all_categories = [category] + list(category.get_all_subcategories())
        category_ids = [c.id for c in all_categories]

        return (
            ProductModel.objects.filter(
                category_id__in=category_ids,
                status=ProductStatusType.publish.value,
            ).aggregate(min_price=Min("price"))["min_price"]
            or 0
        )

    def get_popular_products(self, request):
        products = (
            ProductModel.objects.select_related("category")
            .filter(status=ProductStatusType.publish.value)
            .order_by("-created_date", "-avg_rate")[:3]
        )

        return PopularProductSerializer(
            products, many=True, context={"request": request}
        ).data
