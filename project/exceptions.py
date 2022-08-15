class TooManyRetries(Exception):
    message = 'there was too many retries'

    def __init__(self, message=None):
        if message:
            self.message = message