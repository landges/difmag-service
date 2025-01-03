import os
import urllib.parse
from typing import Optional

import boto3
from botocore.client import Config


class S3Manager:
    """
    Класс-менеджер для работы с AWS S3 через boto3.
    """

    def __init__(
        self,
        bucket_name: str,
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        default_acl: str = "private",
        expiration: int = 3600,
    ):
        """
        :param bucket_name: Название S3-бакета.
        :param region_name: Регион (по умолчанию us-east-1).
        :param aws_access_key_id: Ключ доступа AWS (если не задан, берётся из окружения).
        :param aws_secret_access_key: Секретный ключ AWS.
        :param aws_session_token: Сессионный токен (если используется временная сессия).
        :param endpoint_url: Необязательный кастомный endpoint (например, для S3-совместимых сервисов).
        :param default_acl: ACL (права доступа) по умолчанию при загрузке, например "private" или "public-read".
        :param expiration: Время жизни генерируемых ссылок (presigned URLs) в секундах.
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.default_acl = default_acl
        self.expiration = expiration

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name
        )

        self.s3_client = session.client(
            "s3",
            endpoint_url=endpoint_url,
            config=Config(signature_version="s3v4")
        )
        self.s3_resource = session.resource(
            "s3",
            endpoint_url=endpoint_url,
            config=Config(signature_version="s3v4")
        )
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def upload_file(self, file_path: str, s3_key: str) -> str:
        """
        Загрузить локальный файл file_path в S3 с ключом s3_key.
        Возвращает публичную (или presigned) ссылку на загруженный объект.
        
        :param file_path: Путь к локальному файлу.
        :param s3_key: Ключ в S3 (например, 'folder/myfile.jpg').
        :return: Ссылка (presigned URL), по которой можно скачать файл.
        """
        # Загружаем файл в S3
        self.s3_client.upload_file(
            Filename=file_path,
            Bucket=self.bucket_name,
            Key=s3_key,
            ExtraArgs={"ACL": self.default_acl}
        )

        # Генерируем временную ссылку на скачивание
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=self.expiration
        )
        return presigned_url

    def upload_fileobj(self, fileobj, s3_key: str) -> str:
        """
        Загрузить file-like объект (например, BytesIO) прямо в S3.
        Возвращает presigned URL.
        
        :param fileobj: Открытый файловый объект (например, UploadFile.file в FastAPI).
        :param s3_key: Ключ в S3.
        :return: Presigned URL.
        """
        self.s3_client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self.bucket_name,
            Key=s3_key,
            ExtraArgs={"ACL": self.default_acl}
        )
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=self.expiration
        )
        return presigned_url

    def get_presigned_url(self, s3_key: str, expiration: Optional[int] = None) -> str:
        """
        Получить presigned URL (временную ссылку) к объекту S3.
        :param s3_key: Ключ объекта в бакете.
        :param expiration: Время жизни ссылки в секундах (если не задано, берём self.expiration).
        :return: Presigned URL.
        """
        if expiration is None:
            expiration = self.expiration

        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expiration
        )
        return presigned_url

    def get_filename_from_url(self, url: str) -> str:
        """
        Извлекает значение s3_key (имя файла / ключ) из presigned URL или обычного S3 URL.
        Работает на основе параметров 'Key=' или анализа пути.
        
        :param url: Ссылка (presigned или s3://).
        :return: Ключ (например, 'folder/myfile.jpg').
        """
        # Сперва попробуем распарсить query-params (Key=...)
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)

        # Если есть Key= в запросе, то возьмём оттуда
        if "Key" in query_params:
            return query_params["Key"][0]

        # Иначе попробуем выделить путь (для s3://bucket/key или https://...)
        path = parsed.path
        # Обычно путь может начинаться с /bucket_name/...
        # Если ссылка вида https://bucket.s3.amazonaws.com/folder/file.jpg
        # то path = /folder/file.jpg
        if path.startswith("/"):
            path = path[1:]
        # Если там ещё присутствует имя бакета, отрежем его
        if path.startswith(self.bucket_name + "/"):
            path = path[len(self.bucket_name) + 1:]

        return path

    def download_file(self, url: str, local_path: str) -> None:
        """
        Скачать файл из S3 (presigned или обычная ссылка) в локальный путь local_path.
        
        :param url: Ссылка на объект (presigned URL или https://s3/bucket/key).
        :param local_path: Куда сохранить.
        """
        s3_key = self.get_filename_from_url(url)
        self.s3_client.download_file(
            Bucket=self.bucket_name,
            Key=s3_key,
            Filename=local_path
        )

    def delete_file(self, url: str) -> None:
        """
        Удалить объект из S3 по ссылке (presigned или обычной).
        
        :param url: Ссылка на объект.
        """
        s3_key = self.get_filename_from_url(url)
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )
