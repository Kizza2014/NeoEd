from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom import PostCreate, PostUpdate
from typing import List
from datetime import datetime
from pytz import timezone
from src.service.models.classroom import Comment
from src.service.models.exceptions import ClassroomNotFoundException


TIMEZONE = timezone('Asia/Ho_Chi_Minh')


class PostRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")

    async def get_posts_in_class(self, class_id: str) -> List[dict] | None:
        db_class = self.collection.find_one({'_id': class_id})
        if not db_class:
            raise ClassroomNotFoundException
        return db_class['posts']


    async def get_by_id(self, class_id: str, post_id: str) -> dict | None:
        result = self.collection.find_one({'_id': class_id, 'posts.id': post_id}, {'posts.$': 1})
        if not result:
            return None
        return result['posts'][0]

    async def create_post(self, class_id, new_post: PostCreate) -> bool:
        post_info = new_post.model_dump()
        created_at = datetime.now(TIMEZONE)
        post_info['comments'] = []
        post_info['created_at'] = created_at
        post_info['updated_at'] = created_at
        if new_post.attachments is not None:
            post_info['attachments'] = new_post.attachments
        else:
            post_info['attachments'] = []

        filters = {'_id': class_id}
        updates = {
            '$push': {
                'posts': post_info
            }
        }

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0


    async def update_by_id(self, class_id, post_id, update_data: PostUpdate) -> bool:
        update_data = update_data.model_dump(exclude_unset=True)

        # Prepare additional and removal attachments
        additional_attachments = update_data.pop('additional_attachments', [])
        removal_attachments = update_data.pop('removal_attachments', [])

        filters = {'_id': class_id, 'posts.id': post_id}

        # remove the specified attachments
        if removal_attachments:
            self.collection.update_one(
                filters,
                {'$pull': {'posts.$.attachments': {'$in': removal_attachments}}}
            )

        # add the new attachments
        if additional_attachments:
            self.collection.update_one(
                filters,
                {'$addToSet': {'posts.$.attachments': {'$each': additional_attachments}}}
            )

        # update other fields
        update_fields = {f'posts.$.{k}': v for k, v in update_data.items()}
        update_fields['posts.$.updated_at'] = datetime.now(TIMEZONE)
        result = self.collection.update_one(
            filters,
            {'$set': update_fields}
        )
        return result.modified_count > 0

    async def delete_by_id(self, class_id: str, post_id: str) -> bool:
        result = self.collection.update_one(
            {'_id': class_id},
            {'$pull': {'posts': {'id': post_id}}}
        )
        return result.modified_count > 0

    async def create_comment(self, class_id: str, post_id: str, new_comment: Comment):
        comment_info = new_comment.model_dump()
        comment_info['created_at'] = datetime.now(TIMEZONE)
        comment_info['updated_at'] = datetime.now(TIMEZONE)

        filters = {'_id': class_id, 'posts.id': post_id}
        updates = {
            '$push': {
                'posts.$.comments': comment_info
            }
        }

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0
