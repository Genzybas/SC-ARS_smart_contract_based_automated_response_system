import json
import sys
import unittest
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _load_case(source: str):
    case_file = {
        "nsl": BASE_DIR / "test" / "nsl_kdd_test_samples.json",
        "ton": BASE_DIR / "test" / "test_toniot_samples.json",
        "cicids": BASE_DIR / "test" / "cicids_test_samples.json",
    }[source]
    payload = json.loads(case_file.read_text())
    sample = payload[0]["input"]
    return np.array(sample, dtype=float).reshape(1, -1)


class PredictionInputTests(unittest.TestCase):
    def test_saved_models_accept_their_dataset_samples(self):
        from ml_gateway.main import _prepare_model_input, pipelines

        for source in ("nsl", "ton", "cicids"):
            with self.subTest(source=source):
                X = _load_case(source)
                pipeline = pipelines[source]
                model_input = _prepare_model_input(pipeline, X)
                self.assertEqual(model_input.shape[1], pipeline["model"].n_features_in_)
                self.assertEqual(pipeline["model"].predict(model_input).shape, (1,))
                self.assertEqual(pipeline["model"].predict_proba(model_input).shape[0], 1)


if __name__ == "__main__":
    unittest.main()
