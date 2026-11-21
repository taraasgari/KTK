from shop_core.stores.services import get_user_store


def get_dashboard_context(user):

    store = get_user_store(user)

    return {
        "store": store,
        "store_name": (
            store.name
            if store
            else None
        )
    }