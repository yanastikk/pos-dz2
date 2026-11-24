class DependencyError(LookupError):
    pass


class Container:
    def __init__(self):
        self._factories = {}
        self._is_singleton = {}
        self._singletons = {}
        self._resolving = []

    def register_singleton(self, key, factory):
        self._register(key, factory, True)

    def register_transient(self, key, factory):
        self._register(key, factory, False)

    def register_instance(self, key, instance):
        def factory(container):
            return instance
        self.register_singleton(key, factory)

    def _register(self, key, factory, singleton):
        self._factories[key] = factory
        self._is_singleton[key] = singleton

        if key in self._singletons:
            del self._singletons[key]

    # если объект готов, отдаём, иначе собираем
    def resolve(self, key):
        if key in self._singletons:
            return self._singletons[key]

        if key not in self._factories:
            raise DependencyError("Зависимость не зарегистрирована: " + key.__name__)

        # защита от цикла
        if key in self._resolving:
            chain = ""
            for k in self._resolving:
                chain = chain + k.__name__ + " -> "
            raise DependencyError("Циклическая зависимость: " + chain + key.__name__)

        self._resolving.append(key)
        try:
            instance = self._factories[key](self)
        finally:
            self._resolving.pop()

        if self._is_singleton[key]:
            self._singletons[key] = instance
        return instance
