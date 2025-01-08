from src.repository.mysql.classroom import MySQLClassroomRepository
from src.configs.connections.mysql import get_mysql_connection
from src.repository.mongodb.assignment import AssignmentRepository
from src.repository.mongodb.classroom import MongoClassroomRepository
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from src.configs.connections.mongodb import get_mongo_connection
from pymongo.errors import PyMongoError
from typing import List
from src.service.models.classroom.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from src.configs.connections import SupabaseStorage
from src.service.notification.notification_service import NotificationService
import uuid
from datetime import datetime
from src.service.models.classroom.submission import Submission, Resubmission


ASSIGNMENT_CONTROLLER = APIRouter(tags=['Assignments'])
BUCKET = 'assignments'

# TODO: replace with user from token
current_user = {
    'id': 'user-ffe17039-f1e6-41dd-87f4-659489c4cd0d',
    'username': 'robinblake',
    'fullname': 'robinblake',
    'gender': 'Other',
    'role': 'Teacher'
}

@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/all", response_model=List[AssignmentResponse])
async def get_all_assignments(class_id: str, connection=Depends(get_mongo_connection)) -> List[AssignmentResponse]:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(current_user['id'], class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        repo = AssignmentRepository(connection)
        query_result = await repo.get_all(class_id)
        return [AssignmentResponse(**assgn_dict) for assgn_dict in query_result]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/detail", response_model=AssignmentResponse)
async def get_by_id(class_id: str, assgn_id: str, connection=Depends(get_mongo_connection)) -> AssignmentResponse:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(current_user['id'], class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        repo = AssignmentRepository(connection)
        db_assgn = await repo.get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")

        # get attachments urls
        assignment_folder = class_id + '/' + assgn_id
        storage = SupabaseStorage()
        urls = await storage.get_file_urls(
            bucket_name=BUCKET,
            file_locations=[assignment_folder + '/' + filename for filename in db_assgn['attachments']]
        )
        db_assgn['attachments'] = urls
        return AssignmentResponse(**db_assgn)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.post("/classroom/{class_id}/assignment/create")
async def create_assignment(
        class_id: str,
        title: str = Form(...),
        descriptions: str = Form(...),
        start_at: datetime = Form(None),
        end_at: datetime = Form(None),
        attachments: List[UploadFile] = File(None),
        connection=Depends(get_mongo_connection),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        classroom_repo = MongoClassroomRepository(connection)
        if (not await classroom_repo.find_participant_in_class(current_user['id'], class_id)
                or current_user['role'] != 'Teacher'):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        # create assignment in database
        assignment_dict = {
            'title': title,
            'author': current_user['username'],
            'descriptions': descriptions,
            'start_at': start_at if start_at else None,
            'end_at': end_at if end_at else None,
            'attachments': [attachment.filename for attachment in attachments] if attachments else []
        }
        assignment_dict = {k:v for k, v in assignment_dict.items() if v is not None}
        assgn_id = 'assignment-' + str(uuid.uuid4())
        new_assignment = AssignmentCreate(**assignment_dict, id=assgn_id)

        repo = AssignmentRepository(connection)
        if not await repo.create_assignment(class_id, new_assignment):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to create assignment.")

        # upload attachments to storage
        storage = SupabaseStorage()
        assgn_folder = class_id + "/" + assgn_id
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=attachments if attachments else [],
            dest_folder=assgn_folder
        )

        notification_service = NotificationService(class_id, mysql_cnx)
        notification_service.create_new_notification_for_students(
            title=current_user['username'] + " has created new assignment.",
            content=title,
            direct_url=f"/c/{class_id}/a/{assgn_id}"
        )

        return {
            'message': 'Assignment created successfully',
            'assignment_id': assgn_id,
            'upload_results': upload_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/update")
async def update_by_id(
        class_id: str,
        assgn_id: str,
        title: str = Form(None),
        descriptions: str = Form(None),
        start_at: datetime = Form(None),
        end_at: datetime = Form(None),
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        connection=Depends(get_mongo_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        classroom_repo = MongoClassroomRepository(connection)
        if (not await classroom_repo.find_participant_in_class(current_user['id'], class_id)
                or current_user['role'] != 'Teacher'):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')
        
        # update assignment in database
        information = {
            'title': title if title else None,
            'descriptions': descriptions if descriptions else None,
            'start_at': start_at if start_at else None,
            'end_at': end_at if end_at else None,
            'additional_attachments': [attachment.filename for attachment in additional_attachments] 
                                                if additional_attachments else None,
            'removal_attachments': removal_attachments if removal_attachments else None
        }
        information = {k:v for k,v in information.items() if v is not None}
        update_info = AssignmentUpdate(**information)
        repo = AssignmentRepository(connection)
        status = await repo.update_by_id(class_id, assgn_id, update_info)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to update assignment.")

        # upload and remove attachments
        assignment_folder = class_id + '/' + assgn_id
        storage = SupabaseStorage()
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=additional_attachments if additional_attachments else [],
            dest_folder=assignment_folder
        )

        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[assignment_folder + '/' + filename for filename in removal_attachments]
            if removal_attachments else []
        )
        return {
            'message': 'Assignment updated successfully',
            'assignment_id': assgn_id,
            'upload_results': upload_results,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.delete("/classroom/{class_id}/assignment/{assgn_id}/delete")
async def delete_by_id(class_id: str, assgn_id: str, connection=Depends(get_mongo_connection)) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        classroom_repo = MongoClassroomRepository(connection)
        if (not await classroom_repo.find_participant_in_class(current_user['id'], class_id)
                or current_user['role'] != 'Teacher'):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        repo = AssignmentRepository(connection)
        db_assgn = await repo.get_by_id(class_id, assgn_id)
        status = await repo.delete_by_id(class_id, assgn_id)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to delete assignment.")

        # remove attachments
        assgn_folder = class_id + '/' + assgn_id
        storage = SupabaseStorage()
        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[assgn_folder + '/' + filename for filename in db_assgn['attachments']]
        )

        return {
            'message': f'Deleted assignment successfully',
            'assignment_id': assgn_id,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/submission/all")
async def get_all_submission(class_id: str, assgn_id: str, connection=Depends(get_mongo_connection)) -> List[dict]:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        classroom_repo = MongoClassroomRepository(connection)
        if (not await classroom_repo.find_participant_in_class(current_user['id'], class_id)
                or current_user['role'] != 'Teacher'):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        repo = AssignmentRepository(connection)
        submissions = await repo.get_all_submission(class_id, assgn_id)
        return submissions
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/submission/{student_id}/detail")
async def get_submission(
        class_id: str,
        assgn_id:str,
        student_id: str,
        connection=Depends(get_mongo_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        classroom_repo = MongoClassroomRepository(connection)
        if (not await classroom_repo.find_participant_in_class(current_user['id'], class_id)
                or current_user['role'] != 'Teacher'):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        repo = AssignmentRepository(connection)
        submission = await repo.get_submission(class_id, assgn_id, student_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        return submission
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

# SUBMIT ASSIGNMENT
@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/submit")
async def submit(
        class_id: str,
        assgn_id: str,
        attachments: List[UploadFile] = File(None),
        connection=Depends(get_mongo_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(current_user['id'], class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        # submit assignment
        repo = AssignmentRepository(connection)
        db_assgn = await repo.get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if db_assgn['end_at'] and db_assgn['end_at'] < datetime.now():
            raise HTTPException(status_code=403, detail='Assignment submission is closed.')

        # create submission
        submission = Submission(
            student_id=current_user['id'],
            attachments=[attachment.filename for attachment in attachments],
            submitted_at=datetime.now()
        )
        if not await repo.submit(class_id, assgn_id, submission):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to submit assignment.")

        # upload attachments to storage
        storage = SupabaseStorage()
        submission_folder = class_id + "/" + assgn_id + "/" + current_user['id']
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=attachments if attachments else [],
            dest_folder=submission_folder
        )

        return {
            'message': 'Assignment submitted successfully',
            'assignment_id': assgn_id,
            'upload_results': upload_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/resubmit")
async def resubmit(
        class_id: str,
        assgn_id: str,
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        connection=Depends(get_mongo_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is a participant of the class
        classroom_repo = MongoClassroomRepository(connection)
        if not await classroom_repo.find_participant_in_class(current_user['id'], class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        # resubmit assignment
        repo = AssignmentRepository(connection)
        db_assgn = await repo.get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if db_assgn['end_at'] and db_assgn['end_at'] < datetime.now():
            raise HTTPException(status_code=403, detail='Assignment submission is closed.')

        # ensure user has not been graded
        submission = await repo.get_submission(class_id, assgn_id, current_user['id'])
        if submission and submission.get('grade', None) is not None:
            raise HTTPException(status_code=403, detail='Your submission is already graded. You cannot resubmit.')

        # create resubmission
        resubmission = Resubmission(
            student_id=current_user['id'],
            additional_attachments=[attachment.filename for attachment in additional_attachments]
                                                            if additional_attachments else [],
            removal_attachments=removal_attachments if removal_attachments else [],
            submitted_at=datetime.now()
        )
        if not await repo.resubmit(class_id, assgn_id, resubmission):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to resubmit assignment.")

        # upload attachments to storage
        storage = SupabaseStorage()
        submission_folder = class_id + "/" + assgn_id + "/" + current_user['id']
        upload_results = await storage.bulk_upload(
            bucket_name=BUCKET,
            files=additional_attachments if additional_attachments else [],
            dest_folder=submission_folder
        )

        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[submission_folder + '/' + filename for filename in removal_attachments]
            if removal_attachments else []
        )
        return {
            'message': 'Assignment resubmitted successfully',
            'assignment_id': assgn_id,
            'upload_results': upload_results,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")

@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/submission/{student_id}/grade")
async def grade(
        class_id: str,
        assgn_id: str,
        student_id: str,
        grade: float = Form(...),
        mongo_connection=Depends(get_mongo_connection),
        mysql_connection=Depends(get_mysql_connection)
) -> dict:
    try:
        # TODO: replace with user from token
        # ensure user is logged in
        if not current_user:
            raise HTTPException(status_code=403, detail='Unauthorized. You must login before accessing this resource.')

        # ensure user is teacher of the class
        mysql_classroom_repo = MySQLClassroomRepository(mysql_connection)
        if await mysql_classroom_repo.get_user_role(current_user['id'], class_id) != 'teacher':
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class')

        # grade assignment
        repo = AssignmentRepository(mongo_connection)
        if not await repo.grade(class_id, assgn_id, student_id, grade):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to grade assignment.")

        return {
            'message': 'Assignment graded successfully',
            'assignment_id': assgn_id,
            'student_id': student_id,
            'grade': grade
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")