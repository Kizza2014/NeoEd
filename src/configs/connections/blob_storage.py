from supabase import create_client
from src.configs.utils import get_env_var
import os
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
            upsert='true'):
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
                file_location = os.path.join(dest_folder, file.filename)
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
            # Return failure status with error message
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
    ):
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

    async def remove_files(self, bucket_name: str, file_locations: List[str]):
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
                if status.get("message") == "Success":
                    remove_results.append({'file': file, 'status': 'success'})
                else:
                    remove_results.append({'file': file, 'status': 'failed', 'error': status.get("message")})
        except Exception as e:
            for file in file_locations:
                remove_results.append({'file': file, 'status': 'failed', 'error': str(e)})
        return remove_results

    async def remove_folder(self, bucket_name: str, folder_path: str):
        """
        Removes all files within a specified folder in a Supabase storage bucket.

        Parameters:
        - bucket_name (str): The name of the bucket containing the folder.
        - folder_path (str): The path to the folder to be removed.

        Returns:
        - dict: A dictionary containing the status of the operation and the list of removed files.

        Raises:
        - Exception: If any file removal or folder processing fails, an error message is included in the returned dictionary.
        """
        try:
            # List all files in the folder
            response = self.client.storage.from_(bucket_name).list(folder_path, {'limit': None})
            file_paths = [file['name'] for file in response]

            # Remove all files in the folder
            if file_paths:
                self.client.storage.from_(bucket_name).remove(file_paths)

            return {'status': 'success', 'removed_files': file_paths}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}


    async def get_file_url(self, bucket_name: str, file_location: str, expires_in: int = 86400):
        """
        Generates a signed URL for a file in Supabase storage.

        Parameters:
        - bucket_name (str): The name of the bucket containing the file.
        - file_location (str): The path or location of the file in the bucket.
        - expires_in (int, optional): Number of seconds until the URL expires. Defaults to 86400 (1 day).

        Returns:
        - str: The generated signed URL.

        Raises:
        - Exception: If generating the signed URL fails, raises an exception with error details.
        """
        try:
            response = self.client.storage.from_(bucket_name).create_signed_url(file_location, expires_in)
            return response['signedURL']
        except Exception as e:
            raise Exception(f"Error generating signed URL for file '{file_location}': {str(e)}")

    async def get_file_urls(self, bucket_name: str, file_locations: List[str], expires_in: int = 86400):
        """
        Generates signed URLs for multiple files in Supabase storage.

        Parameters:
        - bucket_name (str): The name of the bucket containing the files.
        - file_locations (List[str]): A list of file paths or locations in the bucket.
        - expires_in (int, optional): Number of seconds until the URLs expire. Defaults to 86400 (1 day).

        Returns:
        - List[dict]: A list of dictionaries containing the file paths and their corresponding signed URLs.

        Raises:
        - Exception: If generating any signed URL fails, the error details are included in the returned list.
        """
        signed_urls = []
        for file_location in file_locations:
            try:
                response = self.client.storage.from_(bucket_name).create_signed_url(file_location, expires_in)
                signed_urls.append({'file': file_location, 'url': response['signedURL']})
            except Exception as e:
                signed_urls.append({'file': file_location, 'url': None, 'error': str(e)})
        return signed_urls


    async def download_file(self, bucket_name: str, file_name: str, download_path: str):
        try:
            response = self.client.storage.from_(bucket_name).download(file_name)
            with open(download_path, "wb") as file:
                file.write(response.content)
            return True
        except Exception as e:
            raise Exception(f"Error downloading file '{file_name}':", e)


