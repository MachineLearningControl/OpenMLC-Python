class Observer(object):

    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
            return True
        return False

    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer(*args, **kwargs)
