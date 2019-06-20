import mimetypes


def is_url_image(url):
    mimetype = mimetypes.guess_type(url)
    return mimetype[0] and mimetype[0].startswith('image')
