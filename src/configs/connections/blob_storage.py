from supabase import create_client
from src.configs.utils import get_env_var


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
    def create_bucket(self, bucket_name: str, public: bool = False):
        try:
            response = self.client.storage.create_bucket(bucket_name, options={"public": public})
            return response
        except Exception as e:
            raise Exception(f"Error creating bucket '{bucket_name}':", e)


    def upload_file(self, bucket_name: str, file_location, file_data):
        try:
            response = self.client.storage.from_(bucket_name).upload(file_location, file_data)
            return response
        except Exception as e:
            raise Exception(f"Error uploading file '{file_location}':", e)


    def get_file_url(self, bucket_name: str, file_location: str):
        try:
            response = self.client.storage.from_(bucket_name).get_public_url(file_location)
            return response
        except Exception as e:
            raise Exception(f"Error generating public URL for file '{file_location}':", e)


    def download_file(self, bucket_name: str, file_name: str, download_path: str):
        try:
            response = self.client.storage.from_(bucket_name).download(file_name)
            with open(download_path, "wb") as file:
                file.write(response.content)
            return True
        except Exception as e:
            raise Exception(f"Error downloading file '{file_name}':", e)


