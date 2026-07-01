import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone


class TestSQSService:
    def test_dispatch_video_job_sends_to_fifo_queue(self):
        with patch("boto3.client") as mock_boto:
            mock_sqs = MagicMock()
            mock_boto.return_value = mock_sqs
            mock_sqs.send_message.return_value = {"MessageId": "msg_123"}

            from app.services.sqs_service import SQSService
            svc = SQSService(queue_url="https://sqs.us-east-1.amazonaws.com/123/test.fifo")
            svc.dispatch_video_job(job_id="job_abc", workspace_id="ws_123")

            mock_sqs.send_message.assert_called_once()
            call_kwargs = mock_sqs.send_message.call_args[1]
            assert "job_abc" in call_kwargs.get("MessageDeduplicationId", "job_abc")
            assert "ws_123" in call_kwargs.get("MessageGroupId", "ws_123")

    def test_receive_jobs_long_polls(self):
        with patch("boto3.client") as mock_boto:
            mock_sqs = MagicMock()
            mock_boto.return_value = mock_sqs
            mock_sqs.receive_message.return_value = {
                "Messages": [
                    {
                        "MessageId": "msg_123",
                        "ReceiptHandle": "handle_abc",
                        "Body": '{"job_id": "job_abc", "workspace_id": "ws_123"}',
                        "Attributes": {"ApproximateReceiveCount": "1"},
                    }
                ]
            }

            from app.services.sqs_service import SQSService
            svc = SQSService(queue_url="https://sqs.us-east-1.amazonaws.com/123/test.fifo")
            messages = svc.receive_jobs()

            assert len(messages) == 1
            call_kwargs = mock_sqs.receive_message.call_args[1]
            assert call_kwargs.get("WaitTimeSeconds", 0) >= 10

    def test_delete_job_removes_message(self):
        with patch("boto3.client") as mock_boto:
            mock_sqs = MagicMock()
            mock_boto.return_value = mock_sqs

            from app.services.sqs_service import SQSService
            svc = SQSService(queue_url="https://sqs.us-east-1.amazonaws.com/123/test.fifo")
            svc.delete_job(receipt_handle="handle_abc")

            mock_sqs.delete_message.assert_called_once_with(
                QueueUrl="https://sqs.us-east-1.amazonaws.com/123/test.fifo",
                ReceiptHandle="handle_abc",
            )


