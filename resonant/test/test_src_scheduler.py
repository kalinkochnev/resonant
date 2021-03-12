import pytest
from source.mic import Source
from source.ml import SourceScheduler
import source.constants as resonant
from source.geometry import SphericalPt
import numpy as np
from typing import List


class MLStub:
    def __init__(self):
        self.analyzed = False
        self.analyze_name = None

    def analyze(self, src: Source):
        self.analyzed = True
        src.name = self.analyze_name


@pytest.fixture
def sources():
    empty_audio = np.zeros(5)
    resonant.SOURCE_MARGIN = SphericalPt.angle_only(5)
    resonant.MAX_ML_SAMPLES = 8
    resonant.MIN_ML_SAMPLES = 6

    sources = [
        Source(30, empty_audio),
        Source(88, empty_audio),
    ]
    return sources



def test_equiv_src_new(sources):
    # This has the sources not machine learning ready
    ml = MLStub()
    scheduler = SourceScheduler(ml)
    scheduler.sources = sources

    new_src = Source(38.1, np.array([1, 1, 1, 1]))
    scheduler.update_equiv_src(new_src)
    assert ml.analyzed is False
    assert new_src.id != -1
    assert new_src in scheduler.sources


def test_equiv_src_existing(sources):
    # This has the sources not machine learning ready
    resonant.MIN_ML_SAMPLES = 10
    ml = MLStub()
    scheduler = SourceScheduler(ml)
    scheduler.sources = sources

    new_src = Source(33, np.array([1, 1, 1, 1]))
    scheduler.update_equiv_src(new_src)

    assert ml.analyzed is False
    assert new_src.id == None
    assert new_src not in scheduler.sources


def test_cycles_reset(sources: List[Source]):
    ml = MLStub()
    ml.analyze_name = "dog"
    scheduler = SourceScheduler(ml)
    scheduler.sources = sources

    new_src = Source(33, np.array([1, 1, 1, 1, 1, 1]))
    source = sources[0]
    source.cycles_lived = 2
    scheduler.update_equiv_src(new_src)
    assert source.cycles_lived == 0


def test_src_filter(sources: List[Source]):
    resonant.CYCLES_TO_LIVE = 3
    sources = [
        Source(60, np.array([1, 1, 1, 1, 1, 1, 1])),
        Source(21, np.array([1, 1, 1, 1, 1, 1, 1])),
    ]
    sources[0].cycles_lived = 2
    sources[1].cycles_lived = 0
    
@pytest.fixture
def count_nan():
    def count(audio):
        unfilled_count = np.count_nonzero(np.isnan(audio))
        return unfilled_count
    return count

def test_updates(count_nan):
    resonant.MIN_ML_SAMPLES = 3
    resonant.MAX_ML_SAMPLES = 8
    src = Source(30, np.array([]))

    assert src.can_ml_analyze is False
    assert count_nan(src.audio) == resonant.MAX_ML_SAMPLES

    additional = np.array([2, 2, 2, 2])
    src.update_audio(additional)
    expected = np.array([2, 2, 2, 2, np.nan, np.nan, np.nan, np.nan])

    assert np.array_equal(src.audio, expected, equal_nan=True) is True
    assert src.can_ml_analyze is True
    assert count_nan(src.audio) == 4
