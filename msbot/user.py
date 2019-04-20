from msbot.user_options import UserOptions

class User:
    def __init__(self, row_tuple):
        (self.user_id, self.last_updated, self.last_spoiled, options_string) = row_tuple
        self.options = UserOptions(options_string)

    def __repr__(self):
        return ("<User object - id: {user_id}, "
                "last_updated: {last_updated}, "
                "last_updated: {last_updated}, "
                "options: {options}>").format(
                    user_id=self.user_id,
                    last_updated=self.last_updated,
                    last_spoiled=self.last_spoiled,
                    options=self.options
                )

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.user_id == other.user_id and
                self.last_updated == self.last_updated and
                self.last_spoiled == other.last_spoiled and
                self.options == other.options)
