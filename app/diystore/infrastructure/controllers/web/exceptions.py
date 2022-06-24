class BadRequest(Exception):
    default_msg = "bad request"
    code = 400

    def __init__(self, msg=None):
        self.msg = msg or self.default_msg
        super().__init__(self.msg)


# 422 Unprocessable Entity Exceptions
class UnprocessableEntity(BadRequest):
    code = 422

    def __init__(self, msg):
        super().__init__(msg)


class InvalidProductID(UnprocessableEntity):
    default_msg = "invalid product id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)


# 401 Not Found Exceptions
class NotFound(BadRequest):
    code = 401

    def __init__(self, msg):
        super().__init__(msg)


class ProductNotFound(NotFound):
    default_msg = "no product associated with the id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)
