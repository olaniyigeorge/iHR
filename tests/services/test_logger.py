import logging
import os
import pytest
from services.logger import logger

def test_logger_has_stream_handler():
    handlers = logger.handlers
    assert any(isinstance(handler, logging.StreamHandler) for handler in handlers), "StreamHandler not found in logger handlers"

def test_logger_has_file_handler():
    handlers = logger.handlers
    assert any(isinstance(handler, logging.FileHandler) for handler in handlers), "FileHandler not found in logger handlers"

def test_logger_file_handler_path():
    handlers = logger.handlers
    file_handler = next((handler for handler in handlers if isinstance(handler, logging.FileHandler)), None)
    assert file_handler is not None, "FileHandler not found in logger handlers"
    assert file_handler.baseFilename == "/logs/server.logs", f"FileHandler path is {file_handler.baseFilename}, expected '/logs/server.logs'"

def test_logger_formatter():
    handlers = logger.handlers
    for handler in handlers:
        assert handler.formatter._fmt == "%(asctime)s - %(levelname)s - %(message)s", "Formatter format is incorrect"

@pytest.fixture(autouse=True)
def cleanup_log_file():
    yield
    if os.path.exists("/logs/server.logs"):
        os.remove("/logs/server.logs")