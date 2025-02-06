from shop.models import ProductModel, ProductStatusType
from cart.models import CartModel, CartItemModel

class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": {}})  

    def update_product_quantity(self, product_id, quantity):
        if product_id in self._cart["items"]:
            self._cart["items"][product_id]["quantity"] = int(quantity)
            self.save()

    def remove_product(self, product_id):
        if product_id in self._cart["items"]:
            del self._cart["items"][product_id]
            self.save()

    def is_product(self, product_id):
        if product_id in self._cart["items"]:
            return True
        return False
    
    def get_product_quantity(self, product_id):
        
        try:
            return self._cart["items"][str(product_id)]["quantity"]
        except:
            return 0


    def add_product(self, product_id):
        if product_id in self._cart["items"]:
            self._cart["items"][product_id]["quantity"] += 1
        else:
            self._cart["items"][product_id] = {"product_id": product_id, "quantity": 1}
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": {}}
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        for item_key in self._cart["items"]:
            item = self._cart["items"][item_key]
            product_obj = ProductModel.objects.get(id=item["product_id"], status=ProductStatusType.publish.value)
            item.update({"product_obj": product_obj, "total_price": item["quantity"] * product_obj.get_price()})
    
        return self._cart["items"]

    def get_total_product_payment_by_discount(self, product_id):
        return self._cart["items"][str(product_id)]["quantity"] * int(ProductModel.objects.get(id=product_id).get_price())





    def get_total_payment_amount(self):
        return sum(item.get("total_price", 0) for item in self._cart["items"].values())

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self._cart["items"].values())

    def save(self):
        self.session.modified = True

    def sync_cart_items_from_db(self, user):
        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        for cart_item in cart_items:
            item_id = str(cart_item.product.id)
            if item_id in self._cart["items"]:
                self._cart["items"][item_id]["quantity"] = cart_item.quantity
            else:
                self._cart["items"][item_id] = {"product_id": item_id, "quantity": cart_item.quantity}
        self.merge_session_cart_in_db(user)
        self.save()

    def merge_session_cart_in_db(self, user):
        cart, created = CartModel.objects.get_or_create(user=user)
        products = {item["product_id"]: item for item in self._cart["items"].values()}

        for item_id, item in products.items():
            product_obj = ProductModel.objects.get(id=item_id, status=ProductStatusType.publish.value)
            cart_item, created = CartItemModel.objects.get_or_create(cart=cart, product=product_obj)
            cart_item.quantity = item["quantity"]
            cart_item.save()

        session_product_ids = products.keys()
        CartItemModel.objects.filter(cart=cart).exclude(product__id__in=session_product_ids).delete()
