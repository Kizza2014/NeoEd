from supabase import create_client


class SupabaseStorage:
    _instance = None


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseStorage, cls).__new__(cls)
            cls._instance.client = create_client('https://hwfsasxsiluyjprgvkic.supabase.co',
                                                 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3ZnNhc3hzaWx1eWpwcmd2a2ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNTcwNjEyOSwiZXhwIjoyMDUxMjgyMTI5fQ.MMZbfCB-IXu7qBsSSeq5Li_brONaPsAHGuYo68z85Fc')
        return cls._instance


storage = SupabaseStorage()

response = storage.client.storage.from_('test').remove(['test_folder/Screenshot from 2024-10-19 15-05-52.png'])
if response:
    print(response)
