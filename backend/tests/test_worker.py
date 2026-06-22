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


class TestHeyGenService:
    def test_submit_video_returns_job_id(self):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"data": {"video_id": "hg_video_123"}}
            mock_post.return_value = mock_resp

            from app.services.heygen_service import HeyGenService
            svc = HeyGenService(api_key="test_key")
            video_id = svc.submit_video(
                avatar_id="avatar_001",
                voice_id="voice_001",
                script="Hello world",
                language="en",
                tone="professional",
            )

            assert video_id == "hg_video_123"
            mock_post.assert_called_once()

    def test_submit_video_returns_none_on_api_error(self):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.json.return_value = {"error": "rate_limited"}
            mock_post.return_value = mock_resp

            from app.services.heygen_service import HeyGenService
            svc = HeyGenService(api_key="test_key")
            video_id = svc.submit_video(
                avatar_id="avatar_001",
                voice_id="voice_001",
                script="Hello world",
                language="en",
                tone="professional",
            )

            assert video_id is None

    def test_check_status_returns_completed(self):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": {"status": "completed", "video_url": "https://cdn.heygen.com/video/test.mp4"}
            }
            mock_get.return_value = mock_resp

            from app.services.heygen_service import HeyGenService
            svc = HeyGenService(api_key="test_key")
            status, url = svc.check_status("hg_video_123")

            assert status == "completed"
            assert url == "https://cdn.heygen.com/video/test.mp4"


class TestWorkerRetryLogic:
    def test_job_exceeding_max_retries_marked_failed(self):
        mock_message = {
            "MessageId": "msg_123",
            "ReceiptHandle": "handle_abc",
            "Body": '{"job_id": "job_abc"}',
            "Attributes": {"ApproximateReceiveCount": "4"},
        }

        with patch("app.services.sqs_service.SQSService") as MockSQS, \
             patch("app.services.heygen_service.HeyGenService") as MockHeyGen:

            mock_sqs = MockSQS.return_value
            mock_db = MagicMock()

            from app.worker import process_message
            process_message(mock_message, mock_db, mock_sqs, MockHeyGen.return_value)

            mock_sqs.delete_job.assert_called_once_with(receipt_handle="handle_abc")
