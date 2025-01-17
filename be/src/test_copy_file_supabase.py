from supabase import create_client
from pytz import timezone
from datetime import datetime


class SupabaseStorage:
    _instance = None
    _SUPABASE_URL = 'https://hwfsasxsiluyjprgvkic.supabase.co'
    _SUPABSE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3ZnNhc3hzaWx1eWpwcmd2a2ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTcwNjEyOSwiZXhwIjoyMDUxMjgyMTI5fQ.MMZbfCB-IXu7qBsSSeq5Li_brONaPsAHGuYo68z85Fc'


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseStorage, cls).__new__(cls)
            cls._instance.client = create_client(cls._SUPABASE_URL, cls._SUPABSE_KEY)
        return cls._instance

    def copy_post_attachments(self, bucket_name: str, src_classroom: str, dest_classroom: str):
        post_folders = self.client.storage.from_(bucket_name).list(src_classroom)
        copy_results = []
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
                    copy_results.append({'src': src_file, 'dest': dest_file, 'status': 'failed'})
        return copy_results

    def list_dir(self, bucket_name, folder_path=''):
        try:
            return self.client.storage.from_(bucket_name).list(folder_path)
        except Exception as e:
            raise Exception(f"Error listing directory '{folder_path}': {str(e)}")

    def get_file_urls(self, bucket_name: str, file_locations, expires_in: int = 86400):
        urls = []
        response = self.client.storage.from_(bucket_name).create_signed_urls(file_locations, expires_in)
        return response

storage = SupabaseStorage()
# print(storage.copy_post_attachments('bucket_test', 'class1', 'class2'))

response = storage.get_file_urls('bucket_test', ['class1/post1/dokumen.pub_introduction-to-parallel-computing-from-algorithms-to-programming-on-state-of-the-art-platforms-9783319988337-3319988336.pdf', 'class1/post1/yeu-cau.docx', 'class1/post1/Screenshot from 2025-01-09 17-40-45.png'])
print(response)