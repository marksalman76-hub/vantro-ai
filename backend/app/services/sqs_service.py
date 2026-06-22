import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

SQS_QUEUE_URL = os.getenv("SQS_JOBS_QUEUE_URL", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _client():
    return boto3.client("sqs", region_name=AWS_REGION)


def is_configured() -> bool:
    return bool(SQS_QUEUE_URL)


def dispatch_video_job(
    job_id: str,
    avatar_id: str,
    voice_id: str,
    script: str,
    language: str,
    tone: str,
) -> bool:
    """
    Publish a video generation job to SQS.
    Returns True on success, False if SQS is not configured or send fails.
    """
    if not is_configured():
        logger.warning("SQS_JOBS_QUEUE_URL not set — job %s will not be processed", job_id)
        return False

    message = {
        "job_id": job_id,
        "avatar_id": avatar_id,
        "voice_id": voice_id,
        "script": script,
        "language": language,
        "tone": tone,
    }
    try:
        _client().send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message),
            MessageGroupId="video-jobs",          # required for FIFO queues
            MessageDeduplicationId=job_id,        # idempotent: same job_id = same message
        )
        logger.info("Dispatched job %s to SQS", job_id)
        return True
    except ClientError as e:
        logger.error("SQS dispatch failed for job %s: %s", job_id, e)
        return False


def receive_jobs(max_messages: int = 10, wait_seconds: int = 20) -> list[dict]:
    """Long-poll SQS for pending video jobs."""
    if not is_configured():
        return []
    try:
        resp = _client().receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_seconds,       # long poll — reduces empty receives
            VisibilityTimeout=900,              # 15 min: max HeyGen generation time
            AttributeNames=["ApproximateReceiveCount"],
        )
        return resp.get("Messages", [])
    except ClientError as e:
        logger.error("SQS receive_message error: %s", e)
        return []


def extend_visibility(receipt_handle: str, seconds: int = 300) -> None:
    """Extend a message's visibility timeout to prevent re-delivery during long processing."""
    if not is_configured():
        return
    try:
        _client().change_message_visibility(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=seconds,
        )
    except ClientError as e:
        logger.warning("Could not extend visibility timeout: %s", e)


def delete_job(receipt_handle: str) -> None:
    """Remove a successfully processed message from the queue."""
    if not is_configured():
        return
    try:
        _client().delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
    except ClientError as e:
        logger.error("SQS delete_message error: %s", e)
