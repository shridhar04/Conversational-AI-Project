import pytest

from conversational_agent.utils.text import chunk_text

def test_chunk_text_basic() -> None:
    text = " ".join(["token"] * 200)
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)

    assert len(chunks) > 1
    assert all(len(c)) <= 50 for c in chunks
    

def test_chunk_text_invalid_overlap() -> None:
    with pytest.raises(ValueError):
       chunk_text("abc",chunk_size=100,chunk_overlap=10)    