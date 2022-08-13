class BadRequest(Exception):
    default_msg = "bad request"
    code = 400

    def __init__(self, msg=None):
        self.msg = msg or self.default_msg
        super().__init__(self.msg)


# 422 Unprocessable Entity Exceptions
class UnprocessableEntity(BadRequest):
    code = 422

    def __init__(self, msg="unprocessable entity"):
        super().__init__(msg)


class InvalidProductID(UnprocessableEntity):
    default_msg = "invalid product id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)


class InvalidCategoryID(UnprocessableEntity):
    default_msg = "invalid category id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)


class InvalidQueryArgument(UnprocessableEntity):
    default_msg = "invalid query argument {text}"

    def __init__(self, msg=None, parameter=None):
        format_text = f"for parameter {parameter}" if parameter else ""
        self.msg = msg or self.default_msg.format(text=format_text)
        super().__init__(self.msg)


class InvalidQueryParameter(UnprocessableEntity):
    default_msg = "invalid query parameter {parameter}"

    def __init__(self, msg=None, parameter=None):
        self.msg = msg or self.default_msg.format(parameter=parameter or "")
        super().__init__(self.msg)


class ParameterMissing(UnprocessableEntity):
    default_msg = "invalid query: missing parameter {parameter}"

    def __init__(self, msg=None, parameter=None):
        self.msg = msg or self.default_msg.format(parameter=parameter or "")
        super().__init__(self.msg)


# 404 Not Found Exceptions
class NotFound(BadRequest):
    code = 404

    def __init__(self, msg):
        super().__init__(msg)


class ProductNotFound(NotFound):
    default_msg = "no product associated with the id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)


class TopCategoryNotFound(NotFound):
    default_msg = "no top category associated with the id {_id}"

    def __init__(self, msg=None, _id=None):
        self.msg = msg or self.default_msg.format(_id=_id if _id else "")
        super().__init__(self.msg)
