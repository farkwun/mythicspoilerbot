class Spoiler:
    def __init__(self, row_tuple):
        (self.image_url, self.attach_id, self.spoiler_id) = row_tuple

    def __repr__(self):
        return ("<Spoiler object - img: {image}, "
                "attach_id: {attach_id}, row_id: {spoiler_id}>").format(
                    image=self.image_url,
                    attach_id=self.attach_id,
                    spoiler_id=self.spoiler_id
                )

    def __eq__(self, other):
        if not isinstance(other, Spoiler):
            return NotImplemented
        return (self.image_url == other.image_url and
                self.attach_id == other.attach_id and
                self.spoiler_id == other.spoiler_id)
