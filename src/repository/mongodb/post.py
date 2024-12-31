from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom.post import PostCreate, PostUpdate
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

    async def create_post(self, class_id, new_post: PostCreate) -> bool:
        post_info = new_post.model_dump()
        created_at = datetime.now()
        post_id = '_'.join([new_post.author, created_at.strftime('%Y-%m-%d_%H:%M:%S')])

        post_info['id'] = post_id
        post_info['created_at'] = created_at
        post_info['updated_at'] = created_at

        filters = {'_id': class_id}
        updates = {
            '$push': {
                'posts': post_info
            }
        }

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0


    async def update_post_by_id(self, class_id, post_id, update_data: PostUpdate) -> bool:
        update_data = update_data.model_dump(exclude_unset=True)
        update_fields = {f'posts.$.{k}': v for k, v in update_data.items()}

        filters = {'_id': class_id, 'posts.id': post_id}
        updates = {
            '$set': update_fields
        }

        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0


    async def delete_post_by_id(self, class_id: str, post_id: str) -> bool:
        result = self.collection.update_one(
            {'_id': class_id},
            {'$pull': {'posts': {'id': post_id}}}
        )
        return result.modified_count > 0
