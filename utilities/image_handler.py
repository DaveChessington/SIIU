import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ImageHandler:
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

    @staticmethod
    def upload_image(file, user_id):
        # validate file type
        _, ext = os.path.splitext(file.name)
        if ext.lower() not in ImageHandler.ALLOWED_EXTENSIONS:
            raise ValueError(f"Extension not allowed: {ext}")

        file_name = f"user-{user_id}-picture{ext.lower()}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'profiles', file_name)
        try:
            #no exception is raised in case the directory already exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True) 
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            return file_name

        except Exception as e:
            logger.error(f"Failed to upload image for user {user_id}: {str(e)}")
            raise

    @staticmethod
    def delete_image(picture_url):
        old_picture_path = os.path.join(settings.MEDIA_ROOT, 'profiles', picture_url)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)
    
        