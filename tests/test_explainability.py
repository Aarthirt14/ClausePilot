from unittest.mock import patch, MagicMock

import pytest

from src.explainability import _get_pipeline_and_explainer, clear_explainer_cache


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    clear_explainer_cache()
    yield
    clear_explainer_cache()


def test_pipeline_and_explainer_are_cached_per_model_dir(tmp_path):
    model_dir = str(tmp_path)

    with patch("src.explainability.pipeline") as mock_pipeline_fn, \
         patch("src.explainability.shap") as mock_shap:
        mock_pipeline_fn.return_value = MagicMock()
        mock_shap.Explainer.return_value = MagicMock()

        first = _get_pipeline_and_explainer(model_dir)
        second = _get_pipeline_and_explainer(model_dir)

        assert mock_pipeline_fn.call_count == 1
        assert mock_shap.Explainer.call_count == 1
        assert first is second


def test_clear_explainer_cache_forces_rebuild(tmp_path):
    model_dir = str(tmp_path)

    with patch("src.explainability.pipeline") as mock_pipeline_fn, \
         patch("src.explainability.shap") as mock_shap:
        mock_pipeline_fn.return_value = MagicMock()
        mock_shap.Explainer.return_value = MagicMock()

        _get_pipeline_and_explainer(model_dir)
        clear_explainer_cache()
        _get_pipeline_and_explainer(model_dir)

        assert mock_pipeline_fn.call_count == 2
