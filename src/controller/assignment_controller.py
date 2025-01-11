from src.configs.connections.mysql import get_mysql_connection
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from src.configs.connections.mongodb import get_mongo_connection
from pymongo.errors import PyMongoError
from typing import List
from src.service.models.classroom.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from src.configs.connections import SupabaseStorage
from src.service.notification.notification_service import NotificationService
import uuid
from datetime import datetime
from pytz import timezone
from src.service.models.classroom.submission import Submission, Resubmission
from src.service.authentication.utils import verify_token
from src.controller.utils import get_mysql_repo, get_mongo_repo


ASSIGNMENT_CONTROLLER = APIRouter(tags=['Assignments'])
BUCKET = 'assignments'


@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/all", response_model=List[AssignmentResponse])
async def get_all_assignments(
        class_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> List[AssignmentResponse]:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        assignments = await mongo_repo['assignment'].get_all(class_id)
        return [AssignmentResponse(**assgn_dict) for assgn_dict in assignments]
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/detail", response_model=AssignmentResponse)
async def get_by_id(
        class_id: str,
        assgn_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> AssignmentResponse:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        db_assgn = await mongo_repo['assignment'].get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")

        # get attachments urls
        assignment_folder = class_id + '/' + assgn_id
        storage = SupabaseStorage()
        urls = await storage.get_file_urls(
            bucket_name=BUCKET,
            file_locations=[assignment_folder + '/' + file['filename'] for file in db_assgn['attachments']]
        )
        db_assgn['attachments'] = urls
        return AssignmentResponse(**db_assgn)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.post("/classroom/{class_id}/assignment/create")
async def create_assignment(
        class_id: str,
        user_id: str=Depends(verify_token),
        title: str = Form(...),
        descriptions: str = Form(...),
        start_at: datetime = Form(None),
        end_at: datetime = Form(None),
        attachments: List[UploadFile] = File(None),
        mongo_cnx=Depends(get_mongo_connection),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher of the class
        if await mysql_repo['classroom'].get_user_role(user_id, class_id) != 'teacher':
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        # create assignment in database
        current_user = await mysql_repo['user'].get_by_id(user_id)
        assignment_dict = {
            'title': title,
            'author': current_user['username'],
            'descriptions': descriptions,
            'start_at': start_at if start_at else None,
            'end_at': end_at if end_at else None,
            'attachments': [{'filename':attachment.filename} for attachment in attachments] if attachments else []
        }
        assignment_dict = {k:v for k, v in assignment_dict.items() if v is not None}
        assgn_id = 'assignment-' + str(uuid.uuid4())
        new_assignment = AssignmentCreate(**assignment_dict, id=assgn_id)
        if not await mongo_repo['assignment'].create_assignment(class_id, new_assignment):
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
        user_id: str=Depends(verify_token),
        title: str = Form(None),
        descriptions: str = Form(None),
        start_at: datetime = Form(None),
        end_at: datetime = Form(None),
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is author of the assignment
        current_user = await mysql_repo['user'].get_by_id(user_id)
        db_assgn = await mongo_repo['assignment'].get_by_id(class_id, assgn_id)
        if current_user['username'] != db_assgn['author']:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be author of this assignment.')
        
        # update assignment in database
        information = {
            'title': title if title else None,
            'descriptions': descriptions if descriptions else None,
            'start_at': start_at if start_at else None,
            'end_at': end_at if end_at else None,
            'additional_attachments': [{'filename':attachment.filename} for attachment in additional_attachments]
                                                if additional_attachments else None,
            'removal_attachments': [{'filename':attachment} for attachment in removal_attachments] if removal_attachments else None
        }
        information = {k:v for k,v in information.items() if v is not None}
        update_info = AssignmentUpdate(**information)
        if not await mongo_repo['assignment'].update_by_id(class_id, assgn_id, update_info):
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
async def delete_by_id(
        class_id: str,
        assgn_id: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is author of the assignment or class owner
        current_user = await mysql_repo['user'].get_by_id(user_id)
        db_assgn = await mongo_repo['assignment'].get_by_id(class_id, assgn_id)
        class_owner = await mysql_repo['classroom'].get_owner(class_id)
        if current_user['username'] != db_assgn['author'] and user_id != class_owner['id']:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be author of this assignment or class owner.')

        status = await mongo_repo['assignment'].delete_by_id(class_id, assgn_id)
        if not status:
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to delete assignment.")

        # remove attachments
        assgn_folder = class_id + '/' + assgn_id
        storage = SupabaseStorage()
        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[assgn_folder + '/' + file['filename'] for file in db_assgn['attachments']]
        )

        return {
            'message': f'Deleted assignment successfully',
            'assignment_id': assgn_id,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


"""
    ASSIGNMENT SUBMISSION
"""
@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/submission/all", response_model=List[dict])
async def get_all_submission(
        class_id: str,
        assgn_id: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> List[dict]:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher of the class
        if await mysql_repo['classroom'].get_user_role(user_id, class_id) != 'teacher':
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class.')

        submissions = await mongo_repo['assignment'].get_all_submission(class_id, assgn_id)
        return submissions
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.get("/classroom/{class_id}/assignment/{assgn_id}/submission/{student_id}/detail", response_model=Submission)
async def get_submission(
        class_id: str,
        assgn_id:str,
        student_id: str,
        user_id: str=Depends(verify_token),
        mysql_cnx=Depends(get_mysql_connection),
        mongo_cnx=Depends(get_mongo_connection)
) -> Submission:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher of the class or student of the submission
        if await mysql_repo['classroom'].get_user_role(user_id, class_id) != 'teacher' and user_id != student_id:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class or student of the submission.')

        submission = await mongo_repo['assignment'].get_submission(class_id, assgn_id, student_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # get attachments urls
        submission_folder = class_id + '/' + assgn_id + '/' + student_id
        storage = SupabaseStorage()
        urls = await storage.get_file_urls(
            bucket_name=BUCKET,
            file_locations=[submission_folder + '/' + file['filename'] for file in submission['attachments']]
        )
        submission['attachments'] = urls
        return Submission(**submission)
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/submit", response_model=dict)
async def submit(
        class_id: str,
        assgn_id: str,
        user_id: str=Depends(verify_token),
        attachments: List[UploadFile] = File(None),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        # submit assignment
        tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        db_assgn = await mongo_repo['assignment'].get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if db_assgn['end_at'] and tz.localize(db_assgn['end_at']) < current_time:
            raise HTTPException(status_code=403, detail='Assignment submission is closed.')

        # create submission
        submission = Submission(
            student_id=user_id,
            attachments=[{'filename':attachment.filename} for attachment in attachments],
            submitted_at=current_time
        )
        if not await mongo_repo['assignment'].submit(class_id, assgn_id, submission):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to submit assignment.")

        # upload attachments to storage
        storage = SupabaseStorage()
        submission_folder = class_id + "/" + assgn_id + "/" + user_id
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

@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/resubmit", response_model=dict)
async def resubmit(
        class_id: str,
        assgn_id: str,
        user_id: str=Depends(verify_token),
        additional_attachments: List[UploadFile] = File(None),
        removal_attachments: List[str] = Form(None),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is a participant of the class
        if not await mongo_repo['classroom'].find_participant_in_class(user_id, class_id):
            raise HTTPException(status_code=403, detail='Unauthorized. You must be a participant of the class.')

        # resubmit assignment
        tz = timezone('Asia/Ho_Chi_Minh')
        current_time = datetime.now(tz)
        db_assgn = await mongo_repo['assignment'].get_by_id(class_id, assgn_id)
        if not db_assgn:
            raise HTTPException(status_code=404, detail="Assignment not found")
        if db_assgn['end_at'] and tz.localize(db_assgn['end_at']) < current_time:
            raise HTTPException(status_code=403, detail='Assignment submission is closed.')

        # ensure user has not been graded
        submission = await mongo_repo['assignment'].get_submission(class_id, assgn_id, user_id)
        if submission and submission.get('grade', None) is not None:
            raise HTTPException(status_code=403, detail='Your submission is already graded. You cannot resubmit.')

        # create resubmission
        resubmission = Resubmission(
            student_id=user_id,
            additional_attachments=[{'filename':attachment.filename} for attachment in additional_attachments]
                                                            if additional_attachments else [],
            removal_attachments=[{'filename':attachment} for attachment in removal_attachments] if removal_attachments else [],
            submitted_at=current_time
        )
        if not await mongo_repo['assignment'].resubmit(class_id, assgn_id, resubmission):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to resubmit assignment.")

        # upload attachments to storage
        storage = SupabaseStorage()
        submission_folder = class_id + "/" + assgn_id + "/" + user_id
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


@ASSIGNMENT_CONTROLLER.delete("/classroom/{class_id}/assignment/{assgn_id}/submission/{student_id}/delete")
async def remove_submission(
        class_id: str,
        assgn_id: str,
        student_id: str,
        user_id: str=Depends(verify_token),
        mongo_cnx=Depends(get_mongo_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is author of submission
        if user_id != student_id:
            raise HTTPException(status_code=403, detail='Unauthorized. You must be author of this submission.')

        # ensure submission is not graded
        db_submission = await mongo_repo['assignment'].get_submission(class_id, assgn_id, student_id)
        if db_submission.get('grade', None) is not None:
            raise HTTPException(status_code=403, detail='Your submission is already graded. You cannot remove it.')

        # remove submission
        if not await mongo_repo['assignment'].remove_submission(class_id, assgn_id, student_id):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to remove submission.")

        # remove attachments
        submission_folder = class_id + '/' + assgn_id + '/' + student_id
        storage = SupabaseStorage()
        remove_results = await storage.remove_files(
            bucket_name=BUCKET,
            file_locations=[submission_folder + '/' + file['filename'] for file in db_submission['attachments']]
        )

        return {
            'message': 'Submission removed successfully',
            'assignment_id': assgn_id,
            'remove_results': remove_results
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")


@ASSIGNMENT_CONTROLLER.put("/classroom/{class_id}/assignment/{assgn_id}/submission/{student_id}/grade")
async def grade_assignment(
        class_id: str,
        assgn_id: str,
        student_id: str,
        user_id: str=Depends(verify_token),
        grade: float = Form(...),
        mongo_cnx=Depends(get_mongo_connection),
        mysql_cnx=Depends(get_mysql_connection)
) -> dict:
    try:
        if not user_id:
            raise HTTPException(status_code=403,
                                detail='Unauthorized. Try to login again before accessing this resource.')

        mysql_repo = await get_mysql_repo(mysql_cnx)
        mongo_repo = await get_mongo_repo(mongo_cnx)

        # ensure user is teacher of the class
        if await mysql_repo['classroom'].get_user_role(user_id, class_id) != 'teacher':
            raise HTTPException(status_code=403, detail='Unauthorized. You must be teacher of this class')

        # grade assignment
        db_user = await mysql_repo['user'].get_by_id(user_id)
        if not await mongo_repo['assignment'].grade(class_id, assgn_id, student_id, grade, db_user['username']):
            raise HTTPException(status_code=500, detail="Unexpected error occurred. Failed to grade assignment.")

        return {
            'message': 'Assignment graded successfully',
            'assignment_id': assgn_id,
            'student_id': student_id,
            'grade': grade,
            'graded_by': db_user['username']
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database MongoDB error: {str(e)}")