"""
process_message helper — importable by tests and the worker service.
"""
import json
import logging

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def process_message(message: dict, db, sqs, heygen) -> None:
    """
    Process a single SQS message.
    If the message has exceeded MAX_RETRIES, mark the job failed and delete it.
    """
    receipt_handle = message["ReceiptHandle"]
    receive_count = int(message.get("Attributes", {}).get("ApproximateReceiveCount", "1"))

    if receive_count > MAX_RETRIES:
        logger.warning("Message exceeded max retries, dropping: %s", message.get("MessageId"))
        try:
            body = json.loads(message.get("Body", "{}"))
            job_id = body.get("job_id")
            if job_id:
                from app.models.workspace import MediaJob
                job = db.query(MediaJob).filter(MediaJob.id == job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = "Exceeded maximum retry count"
                    db.commit()
        except Exception as exc:
            logger.error("Error marking job failed: %s", exc)
        sqs.delete_job(receipt_handle=receipt_handle)
        return

    try:
        body = json.loads(message.get("Body", "{}"))
        job_id = body.get("job_id")
        logger.info("Processing job %s (attempt %s)", job_id, receive_count)
    except Exception as exc:
        logger.error("Failed to parse message body: %s", exc)
        sqs.delete_job(receipt_handle=receipt_handle)
