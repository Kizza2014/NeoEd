from src.service.models.attachment.base_attachment import BaseAttachment


class UrlAttachment(BaseAttachment):
    url_path: str
    attachment_type = 'url'
