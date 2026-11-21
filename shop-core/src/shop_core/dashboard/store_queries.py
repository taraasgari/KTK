def get_store_products(store, Product):

    return Product.objects.filter(
        store=store
    )



def get_store_orders(store, Order):

    return Order.objects.filter(
        store=store
    )



def get_store_customers(store, Customer):

    return Customer.objects.filter(
        store=store
    )