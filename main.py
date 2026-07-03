from functools import lru_cache
import aioboto3

from mypy_boto3_sqs import SQSClient
from asyncio import run
from settings import settings

async def main():
    # połącz z SQS
    # while True:
    #     pobierz wiadomości
    #     przetwórz
    #     usuń z SQS

    session = aioboto3.Session()
    
    async with session.client(
        "sqs",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    ) as sqs:
        while True:
            resp = await sqs.receive_message(
                QueueUrl=settings.sqs_queue_url,
                WaitTimeSeconds=20
            )


if __name__ == "__main__":
    run(main())
