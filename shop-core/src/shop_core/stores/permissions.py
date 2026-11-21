def is_owner(user, store):

    return store.memberships.filter(
        user=user,
        role="owner"
    ).exists()



def can_manage_store(user, store):

    return store.memberships.filter(
        user=user,
        role__in=[
            "owner",
            "admin"
        ]
    ).exists()