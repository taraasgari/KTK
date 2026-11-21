"""Dashboard data services.

Views should call these functions instead of querying tenant models directly.
"""


def get_products(store=None):
    if store is None or not hasattr(store, "products"):
        return []
    return store.products.all()


def get_orders(store=None):
    if store is None or not hasattr(store, "orders"):
        return []
    return store.orders.all()


def get_dashboard_stats(store=None):
    return {
        "products": get_products(store).count() if hasattr(get_products(store), "count") else 0,
        "orders": get_orders(store).count() if hasattr(get_orders(store), "count") else 0,
    }
