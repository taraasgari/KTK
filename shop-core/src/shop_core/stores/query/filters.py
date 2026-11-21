def filter_by_store(queryset, store):
    if store is None:
        return queryset.none()

    return queryset.filter(store=store)