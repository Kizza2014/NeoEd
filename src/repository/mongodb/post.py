from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom import PostCreate, PostUpdate
from typing import List
from datetime import datetime


class PostRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")


    async def get_posts_in_class(self, class_id: str) -> List[dict]:
        db_class = self.collection.find_one({'_id': class_id})
        return db_class['posts']


    async def get_post_by_id(self, class_id: str, post_id: str) -> dict | None:
        db_class = self.collection.find_one({'_id': class_id})
        posts_list = db_class['posts']
        for post in posts_list:
            if post['id'] == post_id:
                return post
        return None

    async def create_post(self, class_id, new_post: PostCreate):
        post_info = new_post.model_dump()
        created_at = datetime.now()
        post_id = '_'.join([new_post.author, created_at.strftime('%Y_%m_%d_%H_%M_%S')])

        post_info['id'] = post_id
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
        if result.modified_count > 0:
            return post_id
        return None


    async def update_post_by_id(self, class_id, post_id, update_data: PostUpdate) -> bool:
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
        update_fields['posts.$.updated_at'] = datetime.now()
        result = self.collection.update_one(
            filters,
            {'$set': update_fields}
        )

        return result.modified_count > 0

    async def delete_post_by_id(self, class_id: str, post_id: str) -> bool:
        result = self.collection.update_one(
            {'_id': class_id},
            {'$pull': {'posts': {'id': post_id}}}
        )
        return result.modified_count > 0
