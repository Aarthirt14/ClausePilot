from unittest.mock import patch, MagicMock

import pytest

from src.inference import assign_severity, load_bert_model, clear_model_cache


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    clear_model_cache()
    yield
    clear_model_cache()


@pytest.mark.parametrize(
    "label,confidence,expected",
    [
        ("Neutral", 0.99, "None"),
        ("Liability Risk", 0.9, "High"),
        ("Liability Risk", 0.7, "Medium"),
        ("Liability Risk", 0.5, "Low"),
        ("Liability Risk", 0.85, "High"),   # boundary: >= 0.85 is High
        ("Liability Risk", 0.65, "Medium"),  # boundary: >= 0.65 is Medium
    ],
)
def test_assign_severity_thresholds(label, confidence, expected):
    assert assign_severity(label, confidence) == expected


def test_load_bert_model_raises_for_missing_directory():
    with pytest.raises(FileNotFoundError):
        load_bert_model(model_dir="this/directory/does/not/exist")


def test_load_bert_model_is_cached_across_calls(tmp_path):
    """
    The whole point of the cache: a second call with the same model_dir
    must not re-read the checkpoint from disk.
    """
    model_dir = str(tmp_path)

    with patch("src.inference.AutoTokenizer") as mock_tokenizer_cls, \
         patch("src.inference.AutoModelForSequenceClassification") as mock_model_cls, \
         patch("src.inference.torch") as mock_torch:
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()
        fake_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = fake_model
        mock_torch.device.return_value = "cpu"
        mock_torch.cuda.is_available.return_value = False

        first = load_bert_model(model_dir=model_dir)
        second = load_bert_model(model_dir=model_dir)

        assert mock_tokenizer_cls.from_pretrained.call_count == 1
        assert mock_model_cls.from_pretrained.call_count == 1
        assert first is second


def test_clear_model_cache_forces_reload(tmp_path):
    model_dir = str(tmp_path)

    with patch("src.inference.AutoTokenizer") as mock_tokenizer_cls, \
         patch("src.inference.AutoModelForSequenceClassification") as mock_model_cls, \
         patch("src.inference.torch") as mock_torch:
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()
        mock_model_cls.from_pretrained.return_value = MagicMock()
        mock_torch.device.return_value = "cpu"
        mock_torch.cuda.is_available.return_value = False

        load_bert_model(model_dir=model_dir)
        clear_model_cache()
        load_bert_model(model_dir=model_dir)

        assert mock_tokenizer_cls.from_pretrained.call_count == 2
