class Spoiler:
    def __init__(self, row_tuple):
        print(row_tuple)
        (self.image_url, self.attach_id, self.row_id) = row_tuple

    def __repr__(self):
        return ("<Spoiler object - img: {image}, "
                "attach_id: {attach_id}, row_id: {row_id}>").format(
                    image=self.image_url,
                    attach_id=self.attach_id,
                    row_id=self.row_id
                )
