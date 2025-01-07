from src.service.checkin.check_in_service import CheckInService
from src.repository.redis.check_in_repository import CheckInRepository

class_id = "classroom-f9c3a80a-474e-40df-8dbd-46492e28435e"
session_id = "ss-12345"

check_in_service = CheckInService(class_id, session_id)
session_id = check_in_service.initialize()

check_in_service.check_in('user-0bea98bd-a2b8-4d08-ac24-d72d3fdcb0f2')


results = check_in_service.collect_redis()
print(results)

check_in_service.destroy()
