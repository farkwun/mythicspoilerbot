class User:
    def __init__(self, row_tuple):
        (self.user_id, self.last_spoiled) = row_tuple

    def __repr__(self):
        return ("<User object - id: {user_id}, "
                "last_spoiled: {last_spoiled}>").format(
                    user_id=self.user_id,
                    last_spoiled=self.last_spoiled
                )

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.user_id == other.user_id and
                self.last_spoiled == other.last_spoiled)
