import json
import msbot.constants

class UserOptions:
    def __init__(self, json_string):
        options = json.loads(json_string)
        if not options:
            options = self.default_options()
        self.set_update_mode(options)
        self.set_duplicates(options)

    def set_update_mode(self, options):
        if msbot.constants.UPDATE_MODE in options:
            self.update_mode = options[msbot.constants.UPDATE_MODE]
        else:
            self.update_mode = self.default_options()[msbot.constants.UPDATE_MODE]

    def set_duplicates(self, options):
        if msbot.constants.DUPLICATES in options:
            self.duplicates = options[msbot.constants.DUPLICATES]
        else:
            self.duplicates = self.default_options()[msbot.constants.DUPLICATES]

    @staticmethod
    def default_options():
        return {
            msbot.constants.UPDATE_MODE: msbot.constants.POLL_MODE_CMD,
            msbot.constants.DUPLICATES: True,
        }

    def to_json(self):
        return {
            msbot.constants.UPDATE_MODE: self.update_mode,
            msbot.constants.DUPLICATES: self.duplicates,
        }

    def to_json_string(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return ("<UserOptions object - update_mode: {update_mode}, duplicates: {duplicates}>"
                .format(
                    update_mode=self.update_mode,
                    duplicates=self.duplicates,
                )
        )

    def __eq__(self, other):
        if not isinstance(other, UserOptions):
            return NotImplemented
        return self.update_mode == other.update_mode
