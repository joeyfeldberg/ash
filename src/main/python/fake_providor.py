class FakeProvidor():
    def __init__(self):
        pass

    def get_all(self):
        return [('test1', '1.1.1.1'), ('test2', '2.2.2.2')]
