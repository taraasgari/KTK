_current_store = None


def set_current_store(store):
    global _current_store
    _current_store = store



def get_current_store():
    return _current_store