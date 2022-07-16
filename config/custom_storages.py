from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):

    # 모든 것은 S3Boto3Storage을 상속받는데 location만 오버라이드한다. 
    location = "static/"
    # 파일을 덮어 저장되지 않도록 한다. 즉, 같은 파일의 경우 업로드 하지 않겠다는 의미이다. 
    file_overwrite = False


class UploadStorage(S3Boto3Storage):

    # 모든 것은 S3Boto3Storage을 상속받는데 location만 오버라이드한다. 
    location = "uploads/"