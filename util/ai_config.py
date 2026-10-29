from cryptography.fernet import Fernet, InvalidToken


def encrypt_api_key(value, secret):
    if not secret:
        raise ValueError('AI configuration encryption is not configured.')
    return Fernet(secret.encode()).encrypt(value.encode()).decode()


def decrypt_api_key(value, secret):
    if not secret:
        raise ValueError('AI configuration encryption is not configured.')
    try:
        return Fernet(secret.encode()).decrypt(value.encode()).decode()
    except (InvalidToken, ValueError) as exc:
        raise ValueError('AI configuration cannot be decrypted.') from exc
