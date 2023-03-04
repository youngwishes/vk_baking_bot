dict_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "vk_bot_formatter": {
            "format": "%(asctime)s | (%(levelname)s) | %(message)s ",
            "datefmt": "%Y-%m-%dT%H:%M:%S"
        },
    },
    "handlers": {
        "vk_bot_handler": {
            "class": "logging.StreamHandler",
            "formatter": "vk_bot_formatter",
            "stream": "ext://sys.stdout"
        },
    },
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": ["vk_bot_handler"]
        },
    }
}
