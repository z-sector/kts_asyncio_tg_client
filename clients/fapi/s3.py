import aiohttp
from aiobotocore.session import get_session

from clients.fapi.uploader import MultipartUploader


class S3Client:
    def __init__(self, endpoint_url: str, aws_access_key_id: str, aws_secret_access_key: str):
        self.session = get_session()
        self.endpoint_url = endpoint_url
        self.key_id = aws_access_key_id
        self.access_key = aws_secret_access_key

    async def upload_file(self, bucket: str, path: str, buffer):
        async with self.session.create_client('s3', region_name='',
                                              endpoint_url=self.endpoint_url,
                                              aws_secret_access_key=self.access_key,
                                              aws_access_key_id=self.key_id) as client:
            await client.put_object(Bucket=bucket, Key=path, Body=buffer)

    async def fetch_and_upload(self, bucket: str, path: str, url: str):
        session_fetch = aiohttp.ClientSession()
        async with session_fetch.request('get', url) as resp:
            if resp.status != 200:
                return

            body = await resp.read()
            await self.upload_file(bucket, path, body)

    async def stream_upload(self, bucket: str, path: str, url: str):
        session_fetch = aiohttp.ClientSession()
        async with session_fetch.request('get', url) as resp:
            if resp.status != 200:
                return

            async with self.session.create_client('s3', region_name='us-west-2',
                                                  endpoint_url=self.endpoint_url,
                                                  aws_secret_access_key=self.access_key,
                                                  aws_access_key_id=self.key_id) as client:
                async with MultipartUploader(client=client, bucket=bucket, key=path) as uploader:
                    chunk = b''
                    async for data in resp.content.iter_chunked(1024 * 1024):
                        chunk += data
                        if len(chunk) > 5 * 1024 * 1024:
                            await uploader.upload_part(data)
                    if chunk:
                        await uploader.upload_part(data)

    async def stream_file(self, bucket: str, path: str, file: str):
        async with self.session.create_client('s3', region_name='us-west-2',
                                              endpoint_url=self.endpoint_url,
                                              aws_secret_access_key=self.access_key,
                                              aws_access_key_id=self.key_id) as client:
            async with MultipartUploader(
                    client=client, bucket=bucket, key=path
            ) as uploader:
                with open(file, 'rb') as fd:
                    buf = fd.read(10 * 1024 * 1024)
                    while buf:
                        await uploader.upload_part(buf)
                        buf = fd.read(10 * 1024 * 1024)
