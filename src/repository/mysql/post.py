from src.repository.mysql.mysql_repository_interface import MysqlRepositoryInterface
from src.configs.utils import fetch_all_as_dict, fetch_one_as_dict
from src.service.models import PostBase
from mysql.connector import Error


class PostRepository(MysqlRepositoryInterface):
    def get_posts_in_class(self, class_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts")
        res = fetch_all_as_dict(cursor)
        return res


    def get_by_id(self, item_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE id LIKE %s", (item_id,))
        res = fetch_one_as_dict(cursor)
        return res


    def update_by_id(self, item_id: str, new_item: PostBase):
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                                    UPDATE posts
                                    SET
                                        id = %s,
                                        title = %s,
                                        class_id = %s,
                                        author = %s,
                                        created_at = %s,
                                        updated_at = %S,
                                        content = %s,
                                    WHERE id LIKE %s
                                    """,
                           (
                               new_item.id,
                               new_item.title,
                               new_item.class_id,
                               new_item.author,
                               new_item.created_at,
                               new_item.updated_at,
                               new_item.content,
                               item_id,
                           )
            )
        except Error:
            return False
        self.connection.commit()
        return cursor.rowcount() > 0

    def delete_by_id(self, item_id: str):
        cursor = self.connection.cursor()
        cursor.execute("DELETE from posts WHERE id LIKE %s", (item_id,))
        self.connection.commit()
        return cursor.rowcount() > 0


    def insert(self, item: PostBase):
        cursor = self.connection.cursor()
        try:
            cursor.execute("INSERT INTO posts VALUE(%s, %s, %s, %s, %s, %s, %s)",
                           (
                               item.id,
                               item.title,
                               item.class_id,
                               item.author,
                               item.created_at,
                               item.updated_at,
                               item.content,
                           )
            )
        except Error:
            return False
        self.connection.commit()
        return cursor.rowcount() > 0