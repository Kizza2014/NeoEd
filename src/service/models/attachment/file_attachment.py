from src.service.models.attachment.base_attachment import BaseAttachment


class FileAttachment(BaseAttachment):
    filepath: str
    attachment_type = 'file'
