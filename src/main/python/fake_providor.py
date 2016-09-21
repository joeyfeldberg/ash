class FakeProvidor():
    def __init__(self):
        pass

    def get_all(self):
        return [('one', '1.1.1.1'), ('two', '2.2.2.2')]
