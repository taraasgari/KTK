from first.models import Product


class ProductService:

    def list_products(self, store):

        return Product.objects.filter(
            store=store
        )


    def get_product(self, store, product_id):

        return Product.objects.filter(
            store=store,
            id=product_id
        ).first()


    def create_product(
        self,
        store,
        data,
        files
    ):

        return Product.objects.create(
            store=store,
            **data
        )