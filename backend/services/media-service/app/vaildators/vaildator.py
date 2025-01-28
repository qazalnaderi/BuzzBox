from fastapi import UploadFile, HTTPException, status
from loguru import logger

def validate_image_file(file: UploadFile, file_type: str = "image"):
    logger.info(f"Validating file: {file.filename} ({file.content_type})")
    ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only JPEG, PNG and GIF are supported."
        )

    try:
        file_size = 0
        while chunk := file.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                logger.error(f"File size exceeds limit: {file_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size too large. Maximum size is 5MB."
                )
        file.file.seek(0)  # Reset file pointer
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error validating file: {str(e)}"
        )
