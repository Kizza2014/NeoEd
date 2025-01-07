from src.repository.mongodb import MongoDBRepositoryInterface
from src.service.models.classroom import AssignmentUpdate, AssignmentCreate
from typing import List
from datetime import datetime
from src.service.models.classroom.submission import Submission, Resubmission


class AssignmentRepository(MongoDBRepositoryInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.collection = self.connection.get_collection("classes")


    async def get_all(self, class_id: str) -> List[dict]:
        db_classroom = self.collection.find_one({'_id': class_id})
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
        created_at = datetime.now()
        assgn_info['created_at'] = created_at
        assgn_info['updated_at'] = created_at

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
        update_fields['assignments.$.updated_at'] = datetime.now()
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
        submission_info['submitted_at'] = datetime.now()
        submission_info['grade'] = None

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
        resubmission_info['submitted_at'] = datetime.now()

        additional_attachments = resubmission_info.pop('additional_attachments', [])
        removal_attachments = resubmission_info.pop('removal_attachments', [])

        filters = {
            '_id': class_id,
            'assignments.id': assgn_id,
            'assignments.submissions.student_id': resubmission_info['student_id']
        }

        # remove the specified attachments
        ok = True
        if removal_attachments:
            response = self.collection.update_one(
                filters,
                {'$pull': {'assignments.$.submissions.$[submission].attachments': {'$in': removal_attachments}}},
                array_filters=[{'submission.student_id': resubmission_info['student_id']}]
            )
            if response.modified_count == 0:
                ok = False

        # add the new attachments
        if additional_attachments:
            response = self.collection.update_one(
                filters,
                {'$addToSet': {
                    'assignments.$.submissions.$[submission].attachments': {'$each': additional_attachments}}},
                array_filters=[{'submission.student_id': resubmission_info['student_id']}]
            )
            if response.modified_count == 0:
                ok = False

        return ok


    async def grade(self, class_id: str, assgn_id: str, student_id: str, grade: float):
        filters = {'_id': class_id, 'assignments.id': assgn_id, 'assignments.submissions.student_id': student_id}
        updates = {
            '$set': {
                'assignments.$.submissions.$[submission].grade': grade
            }
        }
        array_filters = [{'submission.student_id': student_id}]
        response = self.collection.update_one(filters, updates, array_filters=array_filters)
        return response.modified_count > 0


    async def get_all_submission(self, class_id: str, assgn_id: str) -> List[dict]:
        response = self.collection.find_one({'_id': class_id, 'assignments.id': assgn_id}, {'assignments.$': 1})
        return response['assignments'][0]['submissions'] if response else []



    async def get_submission(self, class_id: str, assgn_id: str, student_id: str) -> dict | None:
        response = self.collection.find_one(
            {'_id': class_id, 'assignments.id': assgn_id, 'assignments.submissions.student_id': student_id},
            {'assignments.submissions.$': 1})
        return response['assignments'][0]['submissions'][0] if response else None