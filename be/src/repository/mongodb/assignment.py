from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom import AssignmentUpdate, AssignmentCreate
from typing import List
from datetime import datetime
from src.service.models.classroom.submission import Submission, Resubmission
from pytz import timezone


TIMEZONE = timezone('Asia/Ho_Chi_Minh')

class AssignmentRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")


    async def get_all(self, class_id: str) -> List[dict] | None:
        db_classroom = self.collection.find_one({'_id': class_id})
        if not db_classroom:
            return None
        return db_classroom['assignments']


    async def get_by_id(self, class_id: str, assgn_id: str) -> dict | None:
        db_classroom = self.collection.find_one({'_id': class_id})
        if db_classroom is not None:
            for assignment in db_classroom['assignments']:
                if assignment['id'] == assgn_id:
                    return assignment
        return None


    async def create_assignment(self, class_id: str, new_assgn: AssignmentCreate) -> bool:
        assgn_info = new_assgn.model_dump()
        assgn_info['created_at'] = datetime.now(TIMEZONE)
        assgn_info['updated_at'] = datetime.now(TIMEZONE)
        assgn_info['submissions'] = []
        assgn_info['comments'] = []

        filters = {'_id': class_id}
        updates = {
            '$push': {
                'assignments': assgn_info
            }
        }

        res = self.collection.update_one(filters, updates)
        return res.modified_count > 0


    async def update_by_id(self, class_id: str, assgn_id: str, new_info: AssignmentUpdate) -> bool:
        update_data = new_info.model_dump(exclude_unset=True)

        # Prepare additional and removal attachments
        additional_attachments = update_data.pop('additional_attachments', [])
        removal_attachments = update_data.pop('removal_attachments', [])

        filters = {'_id': class_id, 'assignments.id': assgn_id}

        # remove the specified attachments
        if removal_attachments:
            self.collection.update_one(
                filters,
                {'$pull': {'assignments.$.attachments': {'$in': removal_attachments}}}
            )

        # add the new attachments
        if additional_attachments:
            self.collection.update_one(
                filters,
                {'$addToSet': {'assignments.$.attachments': {'$each': additional_attachments}}}
            )

        # update other fields
        update_fields = {f'assignments.$.{k}': v for k, v in update_data.items()}
        update_fields['assignments.$.updated_at'] = datetime.now(TIMEZONE)
        result = self.collection.update_one(
            filters,
            {'$set': update_fields}
        )

        return result.modified_count > 0

    async def delete_by_id(self, class_id: str, assgn_id: str) -> bool:
        filters = {'_id': class_id}
        updates = {
            '$pull': {
                'assignments': {'id': assgn_id}
            }
        }
        result = self.collection.update_one(filters, updates)
        return result.modified_count > 0


# SUBMIT
    async def submit(self, class_id, assgn_id, submission: Submission) -> bool:
        submission_info = submission.model_dump(exclude_unset=True)
        submission_info['submitted_at'] = datetime.now(TIMEZONE)
        submission_info['grade'] = None
        submission_info['graded_at'] = None
        submission_info['graded_by'] = None

        filters = {'_id': class_id, 'assignments.id': assgn_id}
        updates = {
            '$addToSet': {
                'assignments.$.submissions': submission_info
            }
        }

        response = self.collection.update_one(filters, updates)
        return response.modified_count > 0

    async def resubmit(self, class_id: str, assgn_id: str, resubmission: Resubmission) -> bool:
        resubmission_info = resubmission.model_dump(exclude_unset=True)
        resubmission_info['submitted_at'] = datetime.now(TIMEZONE)

        additional_attachments = resubmission_info.pop('additional_attachments', [])
        removal_attachments = resubmission_info.pop('removal_attachments', [])

        filters = {'_id': class_id, 'assignments.id': assgn_id}
        db_assgn = self.collection.find_one(filters, {'assignments.$': 1})
        db_submission = None
        for submission in db_assgn['assignments'][0]['submissions']:
            if submission['student_id'] == resubmission.student_id:
                db_submission = submission
                break

        if not db_submission:
            return False

        attachments = db_submission.get('attachments', [])
        additional_filenames = set([att['filename'] for att in additional_attachments])
        removal_filenames = set([att['filename'] for att in removal_attachments])
        retain_filenames = set([att['filename'] for att in attachments if att['filename'] not in removal_filenames])

        new_filenames = retain_filenames | additional_filenames
        new_attachments = [{'filename': filename} for filename in new_filenames]

        updates = {
            '$set': {
                'assignments.$.submissions.$[submission].attachments': new_attachments,
                'assignments.$.submissions.$[submission].submitted_at': resubmission_info['submitted_at']
            }
        }
        response = self.collection.update_one(filters, updates, array_filters=[{'submission.student_id': resubmission.student_id}])
        return response.modified_count > 0


    async def grade(self, class_id: str, assgn_id: str, student_id: str, grade: float, graded_by: str):
        current_time = datetime.now(TIMEZONE)
        filters = {'_id': class_id, 'assignments.id': assgn_id, 'assignments.submissions.student_id': student_id}
        updates = {
            '$set': {
                'assignments.$.submissions.$[submission].grade': grade,
                'assignments.$.submissions.$[submission].graded_at': current_time,
                'assignments.$.submissions.$[submission].graded_by': graded_by
            }
        }
        array_filters = [{'submission.student_id': student_id}]
        response = self.collection.update_one(filters, updates, array_filters=array_filters)
        return response.modified_count > 0

    async def get_all_submission(self, class_id: str, assgn_id: str) -> List[dict] | None:
        response = self.collection.find_one(
            {'_id': class_id, 'assignments.id': assgn_id}, {'participants': 1, 'assignments.submissions.$': 1}
        )
        if not response:
            return None

        participants = response.get('participants', [])
        submissions = response['assignments'][0].get('submissions', [])

        students = {}
        for participant in participants:
            if participant['role'] == 'student':
                participant['submitted'] = False
                students[participant['user_id']] = participant

        for submission in submissions:
            student_id = submission['student_id']
            students[student_id]['submitted'] = True
            students[student_id]['submitted_at'] = submission['submitted_at']
            students[student_id]['attachments'] = submission.get('attachments', [])
            if submission['grade'] is not None:
                students[student_id]['grade'] = submission['grade']
            else:
                students[student_id]['grade'] = None
        return students.values()

    async def get_submission(self, class_id: str, assgn_id: str, student_id: str) -> dict | None:
        response = self.collection.find_one(
            {'_id': class_id, 'assignments.id': assgn_id},
            {'assignments.submissions.$': 1})
        if not response:
            return None
        for submission in response['assignments'][0]['submissions']:
            if submission['student_id'] == student_id:
                return submission
        return None

    async def remove_submission(self, class_id: str, assgn_id: str, student_id: str) -> bool:
        filters = {'_id': class_id, 'assignments.id': assgn_id}
        updates = {
            '$pull': {
                'assignments.$.submissions': {'student_id': student_id}
            }
        }

        response = self.collection.update_one(filters, updates)
        return response.modified_count > 0

