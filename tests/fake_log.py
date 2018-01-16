class Fake_log:
    def __getattr__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return None
