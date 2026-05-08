from unittest.mock import Mock, patch

from minimal_jarvis.engine.ollama import OllamaEngine


def test_ollama_engine_generate_success() -> None:
    engine = OllamaEngine()
    mock_response = Mock()
    mock_response.json.return_value = {"response": "4"}
    mock_response.raise_for_status.return_value = None
    with patch("requests.post", return_value=mock_response):
        assert engine.generate("What is 2+2?", 10) == "4"


def test_ollama_engine_generate_error() -> None:
    engine = OllamaEngine()
    import requests
    with patch("requests.post", side_effect=requests.RequestException("boom")):
        output = engine.generate("hi", 10)
        assert "Engine error" in output
