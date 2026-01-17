from fastapi.testclient import TestClient
from src.api import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Mock services to avoid real LLM calls
@patch("src.api.retrieve_context")
@patch("src.api.call_model_generator")
def test_chat_endpoint(mock_generator, mock_retrieve):
    # Setup Mock
    mock_retrieve.return_value = ("Mock Context", {})
    
    # Mock generator to yield chunks
    def mock_gen(*args, **kwargs):
        yield "Hello"
        yield " World"
        
    mock_generator.side_effect = mock_gen

    response = client.post("/chat", json={
        "query": "Hello", 
        "username": "test_user"
    })
    
    assert response.status_code == 200
    # Streaming response verification
    assert response.text == "Hello World"

@patch("src.api.save_feedback")
def test_feedback_endpoint(mock_save):
    response = client.post("/feedback", json={
        "username": "test_user",
        "query": "test query",
        "model": "Initial Model",
        "answer": "test answer",
        "score": 5
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_save.assert_called_once()
