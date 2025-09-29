#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.
class ConfigError(Exception):
    """Error when processing keys from the config file."""

    def __init__(self, file, key, *args):
        super().__init__(args)
        self.file = file
        self.key = key

    def __str__(self):
        return f"Invalid or missing key in config file {self.file}: {self.key}"


class InitializationError(Exception):
    """Sequencing error - trying to initialize the app before configuring it."""

    def __init__(self, *args):
        super().__init__(args)

    def __str__(self):
        return "cannot initialize app before configuring it"
