from .design_models import StoreDesign


def get_design(store):

    design, _ = StoreDesign.objects.get_or_create(
        store=store
    )

    return design



def update_design(store, data):

    design = get_design(store)

    for key, value in data.items():
        setattr(
            design,
            key,
            value
        )

    design.save()

    return design