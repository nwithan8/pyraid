import base64


def encode_username_password(username: str, password: str):
    string = f"{username}:{password}"
    bytes_string = string.encode('ascii')
    encoded_bytes_string = base64.b64encode(bytes_string)
    return encoded_bytes_string.decode('ascii')
