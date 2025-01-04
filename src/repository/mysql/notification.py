from src.repository.mysql import MysqlRepositoryInterface


class NotificationRepository(MysqlRepositoryInterface):
    def get_by_id(self, item_id: str):
        query = """
        SELECT `notifications`.`notification_id`,
        `notifications`.`title`,
        `notifications`.`content`,
        `notifications`.`direct_url`,
        `notifications`.`class_id`,
        `notifications`.`created_at`
        FROM `neoed`.`notifications`
        WHERE notification_id = %s

        """
        try:
            self.cursor.execute(query, (item_id,))
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            raise e

    def update_by_id(self, item_id: str, new_item):
        raise NotImplementedError()

    def delete_by_id(self, item_id: str):
        raise NotImplementedError()

    def insert(self, item):
        query = """
        INSERT INTO `notifications`
        (`notification_id`,
        `title`,
        `content`,
        `direct_url`,
        `class_id`,
        `created_at`)
        VALUES
        (%s, %s, %s, %s, %s, %s)

        """
        try:
            self.cursor.execute(query, (item.notification_id,
                                        item.title,
                                        item.content,
                                        item.direct_url,
                                        item.class_id,
                                        item.created_at))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)

    def queue_notifications_for_students(self, item):
        query = """
        INSERT INTO `users_notifications_status` (`user_id`, `notification_id`, `read_status`)
        SELECT u.id,
               %s,
               0 AS read_status
        FROM users_classes uc
        JOIN users u ON u.id = uc.user_id
        WHERE uc.class_id = %s
        AND u.role = 'Student';
        """
        try:
            self.cursor.execute(query, (item.notification_id, item.class_id))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)

    def get_notifications_of_user(self, user_id: str):
        query = """
        SELECT `users_notifications_status`.`user_id`,
        `users_notifications_status`.`notification_id`,
        `users_notifications_status`.`read_status`
        FROM `users_notifications_status`
        WHERE 
        `users_notifications_status`.`user_id` = %s
        """

        self.cursor.execute(query, (user_id, ))
        rows = self.cursor.fetchall()
        return rows
