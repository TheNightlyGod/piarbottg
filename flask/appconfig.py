import os

class Config:
    SECRET_KEY = 'lolkekhztiposecretkey'
    UPLOAD_FOLDER = './uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Ограничение на размер файла 16MB