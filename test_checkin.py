import uuid

from src.service.checkin.check_in_service import CheckInService

class_id = "classroom-f9c3a80a-474e-40df-8dbd-46492e28435e"
session_id = "ss-" + str(uuid.uuid4())
creator_id = "user-08d5e86f-ac1b-42e8-87c8-9c842854aaaf"
duration = 60 * 5

check_in_service = CheckInService(class_id, session_id, creator_id, duration)
session_id = check_in_service.initialize()

check_in_service.check_in('user-0bea98bd-a2b8-4d08-ac24-d72d3fdcb0f2')
check_in_service.check_in('user-08d5e86f-ac1b-42e8-87c8-9c842854aaaf')


results = check_in_service.synchronize_mysql()
print(results)

check_in_service.destroy()
