from unittest.mock import AsyncMock
from main import process_message


async def test_invalid_json_deletes_message(mock_pool, mock_sqs):
    msg = {"Body": "not json{{{", "ReceiptHandle": "rh1"}
    await process_message(mock_pool, mock_sqs, msg)
    mock_sqs.delete_message.assert_awaited_once()


async def test_duplicate_event_skipped(
    mock_pool, mock_sqs, valid_notification_body, make_sqs_message, mocker
):
    mocker.patch("main.try_mark_processed", return_value=False)
    save_mock = mocker.patch("main.save_notifications", new=AsyncMock())
    msg = make_sqs_message(valid_notification_body)
    await process_message(mock_pool, mock_sqs, msg)
    mock_sqs.delete_message.assert_awaited_once()
    save_mock.assert_not_called()


async def test_happy_path_sends_email(
    mock_pool, mock_sqs, valid_notification_body, make_sqs_message, mocker
):
    mocker.patch("main.try_mark_processed", return_value=True)
    mocker.patch("main.save_notifications", new=AsyncMock())
    mocker.patch("main.get_user_emails", return_value=["a@example.com"])
    send_mock = mocker.patch("main.send_notification_email", new=AsyncMock())
    msg = make_sqs_message(valid_notification_body)
    await process_message(mock_pool, mock_sqs, msg)
    send_mock.assert_awaited_once()
    mock_sqs.delete_message.assert_awaited_once()


async def test_exception_keeps_message_in_sqs(
    mock_pool, mock_sqs, valid_notification_body, make_sqs_message, mocker
):
    mocker.patch("main.try_mark_processed", return_value=True)
    mocker.patch("main.save_notifications", side_effect=Exception("boom"))
    unmark_mock = mocker.patch("main.unmark_processed", new=AsyncMock())
    msg = make_sqs_message(valid_notification_body)
    await process_message(mock_pool, mock_sqs, msg)
    unmark_mock.assert_awaited_once()
    mock_sqs.delete_message.assert_not_called()


async def test_invalid_notification_schema_deletes_message(
    mock_pool, mock_sqs, make_sqs_message
):
    msg = make_sqs_message({"eventId": "not-a-uuid"})

    await process_message(mock_pool, mock_sqs, msg)

    mock_sqs.delete_message.assert_awaited_once()


async def test_no_recipient_emails_skips_sending_and_deletes_message(
    mock_pool, mock_sqs, valid_notification_body, make_sqs_message, mocker
):
    mocker.patch("main.try_mark_processed", return_value=True)
    mocker.patch("main.save_notifications", new=AsyncMock())
    mocker.patch("main.get_user_emails", return_value=[])
    send_mock = mocker.patch("main.send_notification_email", new=AsyncMock())
    msg = make_sqs_message(valid_notification_body)

    await process_message(mock_pool, mock_sqs, msg)

    send_mock.assert_not_awaited()
    mock_sqs.delete_message.assert_awaited_once()


async def test_email_failure_keeps_message_for_retry(
    mock_pool, mock_sqs, valid_notification_body, make_sqs_message, mocker
):
    mocker.patch("main.try_mark_processed", return_value=True)
    mocker.patch("main.save_notifications", new=AsyncMock())
    mocker.patch("main.get_user_emails", return_value=["student@example.com"])
    mocker.patch(
        "main.send_notification_email",
        new=AsyncMock(side_effect=RuntimeError("SMTP unavailable")),
    )
    unmark_mock = mocker.patch("main.unmark_processed", new=AsyncMock())
    msg = make_sqs_message(valid_notification_body)

    await process_message(mock_pool, mock_sqs, msg)

    unmark_mock.assert_awaited_once()
    mock_sqs.delete_message.assert_not_called()
