from supabase import create_client
from src.configs.utils import get_env_var
from typing import List
from fastapi import UploadFile


class SupabaseStorage:
    _instance = None
    _SUPABASE_URL = get_env_var('SUPABASE_URL')
    _SUPABSE_KEY = get_env_var('SUPABASE_KEY')


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseStorage, cls).__new__(cls)
            cls._instance.client = create_client(cls._SUPABASE_URL, cls._SUPABSE_KEY)
        return cls._instance


    # === BLOB STORAGE OPERATIONS ===
    async def create_bucket(self, bucket_name: str, public: bool = False):
        """
        Creates a new bucket in Supabase storage.

        Parameters:
        - bucket_name (str): The name of the bucket to be created.
        - public (bool, optional): Determines if the bucket will be publicly accessible. Defaults to False.

        Returns:
        - dict: The response from Supabase for the create bucket operation.

        Raises:
        - Exception: If the bucket creation fails, it will raise an exception with the error details.
        """
        try:
            return self.client.storage.create_bucket(bucket_name, options={"public": public})
        except Exception as e:
            raise Exception(f"Error creating bucket '{bucket_name}': {str(e)}")

    async def upload_file(
            self,
            bucket_name: str,
            file: UploadFile,
            dest_folder=None,
            upsert='true') -> dict:
        """
        Uploads a single file to the specified Supabase storage bucket.

        Parameters:
        - bucket_name (str): The name of the bucket where the file will be uploaded.
        - file (UploadFile): The file object to be uploaded.
        - dest_folder (str, optional): The target folder in the bucket where the file will be stored. Defaults to None.
        - upsert (str, optional): Indicates whether to overwrite existing files with the same name. Defaults to 'true'.

        Returns:
        - dict: A dictionary containing the file name, status of the upload, and any error messages (if applicable).
        """
        try:
            # Define file location in the bucket
            if dest_folder:
                file_location = dest_folder + "/" + file.filename
            else:
                file_location = file.filename

            # Read file data in binary
            file_data = await file.read()

            # Upload the file to Supabase storage
            self.client \
                .storage \
                .from_(bucket_name) \
                .upload(file_location, file_data, {'content-type': file.content_type, 'upsert': upsert})

            # Return success status
            return {
                'file': file.filename,
                'status': 'success'
            }
        except Exception as e:
            return {
                'file': file.filename,
                'status': 'failed',
                'error': str(e)
            }

    async def bulk_upload(
            self,
            bucket_name: str,
            files: List[UploadFile],
            dest_folder: str = None,
            upsert: str = 'true'
    ) -> List[dict]:
        """
        Uploads multiple files to the specified Supabase storage bucket.

        Parameters:
        - bucket_name (str): The name of the bucket where files will be uploaded.
        - files (List[UploadFile]): A list of file objects to be uploaded.
        - dest_folder (str, optional): The target folder in the bucket where files will be stored. Defaults to None.
        - upsert (str, optional): Indicates whether to overwrite existing files with the same name. Defaults to 'true'.

        Returns:
        - List[dict]: A list of dictionaries containing the results for each file upload.
        """
        upload_results = []
        for file in files:
            upload_result = await self.upload_file(bucket_name, file, dest_folder, upsert)
            upload_results.append(upload_result)

        return upload_results

    async def remove_files(self, bucket_name: str, file_locations: List[str]) -> List[dict]:
        """
        Removes multiple files from the specified Supabase storage bucket.

        Parameters:
        - bucket_name (str): The name of the bucket from where the files will be removed.
        - file_locations (List[str]): A list of file paths to be removed within the bucket.

        Returns:
        - List[dict]: A list of dictionaries containing the results for each file removal.
        """
        remove_results = []
        try:
            response = self.client.storage.from_(bucket_name).remove(file_locations)
            for file, status in zip(file_locations, response):
                if status:
                    remove_results.append({'file': file, 'status': 'success'})
                else:
                    remove_results.append({'file': file, 'status': 'failed', 'error': status.get("message")})
        except Exception as e:
            for file in file_locations:
                remove_results.append({'file': file, 'status': 'failed', 'error': str(e)})
        return remove_results

    async def copy_post_attachments(self, bucket_name: str, src_classroom: str, dest_classroom: str):
        copy_results = []
        list_dir = self.client.storage.from_(bucket_name).list(src_classroom)
        post_folders = [p for p in list_dir if p['id'] is None]
        for folder in post_folders:
            src_folder = f"{src_classroom}/{folder['name']}"
            dest_folder = f"{dest_classroom}/{folder['name']}"
            attachments = self.client.storage.from_(bucket_name).list(src_folder)
            for attachment in attachments:
                src_file = f"{src_folder}/{attachment['name']}"
                dest_file = f"{dest_folder}/{attachment['name']}"
                try:
                    self.client.storage.from_(bucket_name).copy(src_file, dest_file)
                    copy_results.append({'src': src_file, 'dest': dest_file, 'status': 'success'})
                except Exception as e:
                    copy_results.append({'src': src_file, 'dest': dest_file, 'status': 'failed', 'error': str(e)})
        return copy_results

    async def copy_assignment_attachments(self, bucket_name: str, src_classroom: str, dest_classroom: str):
        copy_results = []
        list_dir = self.client.storage.from_(bucket_name).list(src_classroom)
        assgn_folder = [p for p in list_dir if p['id'] is None]
        for folder in assgn_folder:
            src_folder = f"{src_classroom}/{folder['name']}"
            dest_folder = f"{dest_classroom}/{folder['name']}"
            attachments = self.client.storage.from_(bucket_name).list(src_folder)
            for attachment in attachments:
                src_file = f"{src_folder}/{attachment['name']}"
                dest_file = f"{dest_folder}/{attachment['name']}"
                try:
                    self.client.storage.from_(bucket_name).copy(src_file, dest_file)
                    copy_results.append({'src': src_file, 'dest': dest_file, 'status': 'success'})
                except Exception as e:
                    copy_results.append({'src': src_file, 'dest': dest_file, 'status': 'failed', 'error': str(e)})
        return copy_results

    async def get_file_url(self, bucket_name: str, file_location: str, expires_in: int = 86400):
        return self.client.storage.from_(bucket_name).create_signed_url(file_location, expires_in)

    async def get_file_urls(self, bucket_name: str, file_locations: List[str], expires_in: int = 86400) -> List[dict]:
        return self.client.storage.from_(bucket_name).create_signed_urls(file_locations, expires_in)

    async def download_file(self, bucket_name: str, file_name: str, download_path: str):
        try:
            response = self.client.storage.from_(bucket_name).download(file_name)
            with open(download_path, "wb") as file:
                file.write(response.content)
            return True
        except Exception as e:
            raise Exception(f"Error downloading file '{file_name}':", e)


