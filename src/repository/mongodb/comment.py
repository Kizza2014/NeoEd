from src.repository.mongodb.mongodb_repository import MongoDBRepositoryInterface
from src.service.models.classroom import Comment
from pytz import timezone
from typing import List
from datetime import datetime

TIMEZONE = timezone('Asia/Ho_Chi_Minh')

class CommentRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")

    async def get_all(self, class_id: str, item_id: str):
        type = item_id.split('-')[0]
        if type == 'post':
            filters = {'_id': class_id, 'posts.id': item_id}
            result = self.collection.find_one(filters, {'posts.$': 1})
            if result is not None:
                return result['posts'][0].get('comments', [])
        elif type == 'assignment':
            filters = {'_id': class_id, 'assignments.id': item_id}
            result = self.collection.find_one(filters, {'assignments.$': 1})
            if result is not None:
                return result['assignments'][0].get('comments', [])
        return None

    async def get_by_id(self, class_id: str, item_id: str, comment_id: str) -> dict | None:
        type = item_id.split('-')[0]
        if type == 'post':
            filters = {'_id': class_id, 'posts.id': item_id}
            result = self.collection.find_one(filters, {'posts.comments.$': 1})
            if result is not None:
                comments = result['posts'][0].get('comments', [])
                for cmt in comments:
                    if cmt['id'] == comment_id:
                        return cmt
        elif type == 'assignment':
            filters = {'_id': class_id, 'assignments.id': item_id, 'assignments.comments.id': comment_id}
            result = self.collection.find_one(filters, {'assignments.comments.$': 1})
            if result is not None:
                comments = result['assignments'][0].get('comments', [])
                for cmt in comments:
                    if cmt['id'] == comment_id:
                        return cmt
        return None

    async def create_comment(self, class_id: str, item_id: str, comment: Comment):
        comment_info = comment.model_dump()
        current_time = datetime.now(TIMEZONE)
        comment_info['created_at'] = current_time
        comment_info['updated_at'] = current_time

        type = item_id.split('-')[0]
        if type == 'post':
            filters = {'_id': class_id, 'posts.id': item_id}
            updates = {
                '$push': {
                    'posts.$.comments': comment_info
                }
            }
        elif type == 'assignment':
            filters = {'_id': class_id, 'assignments.id': item_id}
            updates = {
                '$push': {
                    'assignments.$.comments': comment_info
                }
            }

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0

    async def update_comment(self, class_id: str, item_id: str, comment_id: str, new_content: str):
        current_time = datetime.now(TIMEZONE)
        type = item_id.split('-')[0]
        if type == 'post':
            filters = {'_id': class_id, 'posts.id': item_id, 'posts.comments.id': comment_id}
            updates = {
                '$set': {
                    'posts.$.comments.$[comment].content': new_content,
                    'posts.$.comments.$[comment].updated_at': current_time
                }
            }
        elif type == 'assignment':
            filters = {'_id': class_id, 'assignments.id': item_id, 'assignments.comments.id': comment_id}
            updates = {
                '$set': {
                    'assignments.$.comments.$[comment].content': new_content,
                    'assignments.$.comments.$[comment].updated_at': current_time
                }
            }

        result = self.collection.update_one(
            filters,
            updates,
            array_filters=[{'comment.id': comment_id}]
        )
        return result.modified_count > 0

    async def delete_comment(self, class_id: str, item_id: str, comment_id: str):
        type = item_id.split('-')[0]
        if type == 'post':
            filters = {'_id': class_id, 'posts.id': item_id, 'posts.comments.id': comment_id}
            updates = {
                '$pull': {
                    'posts.$.comments': {'id': comment_id}
                }
            }
        elif type == 'assignment':
            filters = {'_id': class_id, 'assignments.id': item_id, 'assignments.comments.id': comment_id}
            updates = {
                '$pull': {
                    'assignments.$.comments': {'id': comment_id}
                }
            }
        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0