from shop_core.stores.permissions import can_manage_store


def has_dashboard_access(user, store):

    if not user.is_authenticated:
        return False

    if store is None:
        return False

    return can_manage_store(
        user,
        store
    )