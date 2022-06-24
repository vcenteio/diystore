class OrmEntityNotFullyLoaded(Exception):
    default_msg = "ORM entity not fully loaded"
    def __init__(self, msg=None):
        self.msg = msg or self.default_msg
        super().__init__(self.msg)
