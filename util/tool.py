import random
import string


def random_str(length):
    return ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(length)])