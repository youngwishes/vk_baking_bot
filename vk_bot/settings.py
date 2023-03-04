from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_PATH = Path.joinpath(BASE_DIR, 'media')

DB_PATH = Path.joinpath(BASE_DIR, 'vk_bot', 'db')
