import pytest
from openai import APIConnectionError

from ..llm_provider import LLMGenerationError, OpenAILLMProvider


def test_extract_json_parses_clean_json():
    result = OpenAILLMProvider._extract_json('{"steps": []}')
    assert result == {"steps": []}


def test_extract_json_parses_json_wrapped_in_prose():
    text = 'Here is the result:\n{"steps": [{"action": "click"}]}\nThanks.'
    result = OpenAILLMProvider._extract_json(text)
    assert result == {"steps": [{"action": "click"}]}


def test_extract_json_returns_empty_dict_on_garbage():
    assert OpenAILLMProvider._extract_json("not json at all") == {}


def test_extract_json_returns_empty_dict_on_none():
    assert OpenAILLMProvider._extract_json(None) == {}


def test_api_failure_raises_clean_llm_generation_error_not_raw_sdk_exception():
    import httpx

    provider = OpenAILLMProvider(api_key="fake-key-for-test")

    def raise_connection_error(*args, **kwargs):
        raise APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))

    provider.client.chat.completions.create = raise_connection_error

    with pytest.raises(LLMGenerationError, match="OpenAI request failed"):
        provider.generate("some prompt")
