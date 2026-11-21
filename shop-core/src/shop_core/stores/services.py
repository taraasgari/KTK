from .models import StoreMembership


def get_user_stores(user):
    return (
        StoreMembership.objects
        .filter(user=user)
        .select_related("store")
    )


def get_user_store(user):
    membership = (
        get_user_stores(user)
        .first()
    )

    if membership:
        return membership.store

    return None