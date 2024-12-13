from pymongo import MongoClient

mongo = MongoClient(
    'mongodb+srv://hoangkimgiapt67:1@cluster0.9qjrqzm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=300000,
    waitQueueTimeOutMS=5000
)


def get_mongodb():
    try:
        db = mongo['neoed']
        yield db
    except Exception as e:
        print(e)