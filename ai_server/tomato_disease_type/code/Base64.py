import PIL.Image
import io
import base64

def base64str_file_to_image(base64str_file):
    assert base64str_file is not None
    assert isinstance(base64str_file, str)

    base64_file_bytes = base64str_file.encode('utf-8')
    image = PIL.Image.open(io.BytesIO(base64.b64decode(base64_file_bytes)))

    return image

def get_base64str_file(path):
    assert path is not None
    assert isinstance(path, str)

    base64str_file = None
    with open(path, 'rb') as file:
        base64_file_bytes = base64.b64encode(file.read())
        base64str_file = base64_file_bytes.decode('utf-8')

    assert base64str_file is not None
    return base64str_file