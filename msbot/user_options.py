import json
import msbot.constants

class UserOptions:
    def __init__(self, json_string):
        options = json.loads(json_string)
        if not options:
            options = self.default_options()
        self.update_mode = options[msbot.constants.UPDATE_MODE]

    @staticmethod
    def default_options():
        return {
            msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD
        }

    def to_json(self):
        return {
            msbot.constants.UPDATE_MODE: self.update_mode
        }

    def to_json_string(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return ("<UserOptions object - update_mode: {update_mode}>"
                .format(
                    update_mode=self.update_mode
                )
        )

    def __eq__(self, other):
        if not isinstance(other, UserOptions):
            return NotImplemented
        return self.update_mode == other.update_mode
