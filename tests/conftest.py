import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
URG_SAMPLE = os.path.join(FIXTURES, "urg_sample")


@pytest.fixture
def urg_sample_dir():
    return URG_SAMPLE


@pytest.fixture
def sample_matrix():
    """Two windows: 0_10 passes, 10_20 fails. Line 16 is the faulty one."""
    data = {
        "0_10": [1, 1, 1, 0, 1, 1, 1, 1],
        "10_20": [1, 1, 1, 1, 1, 0, 0, 1],
    }
    index = [
        "updown_counter_12",
        "updown_counter_13",
        "updown_counter_15",
        "updown_counter_16",
        "updown_counter_17",
        "updown_counter_18",
        "updown_counter_19",
        "updown_counter_23",
    ]
    matrix = pd.DataFrame(data, index=index)
    matrix.loc["error"] = [0, 1]
    return matrix
