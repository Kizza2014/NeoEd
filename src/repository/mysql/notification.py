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
            cursor = self.connection.cursor
            cursor.execute(query, (item_id,))
            row = cursor.fetchone()
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
            cursor = self.connection.cursor
            cursor.execute(query, (item.notification_id,
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
            cursor = self.connection.cursor
            cursor.execute(query, (item.notification_id, item.class_id))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)

    def get_notifications_of_user(self, user_id: str):
        query = """
        SELECT notifications.*, users_notifications_status.read_status
        FROM `users_notifications_status`
        JOIN notifications
        ON `users_notifications_status`.`notification_id` = notifications.notification_id
        WHERE 
        `users_notifications_status`.`user_id` = %s;
        """
        cursor = self.connection.cursor
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return rows

    def set_read_status(self, user_id: str, notification_id: str, status: bool):
        query = """
        UPDATE `users_notifications_status`
        SET
        `read_status` = %s
        WHERE `user_id` = %s AND `notification_id` = %s

        """
        try:
            cursor = self.connection.cursor
            cursor.execute(query, (status, user_id, notification_id))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e