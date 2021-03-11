from queue import Queue
from source.geometry import SphericalPt
from source.mic import Source
import numpy as np
import source.constants as resonant
from typing import List, Iterable


class ML:
    options = ['car honk', 'drilling', 'air conditioning', ]

    def analyze(self, source: Source) -> Source:
        """This decides whether to mark a sound as conclusive or not"""
        source.name = "car honk"
        return source

    def is_confident(self, ml_results: dict):
        confidences: np.ndarray = np.array(ml_results.values())
        standardize = lambda value: (value - confidences.mean())/confidences.std()
        max_conf = max(confidences, key=ml_results.get)
        return max_conf >= resonant.ML_CONF_THRESH

class SourceScheduler:
    def __init__(self, ml: ML):
        self.sources: List[Source] = []
        self.ml = ml

    @property
    def identified(self) -> Iterable[Source]:
        return filter(lambda src: src.is_identified, self.sources)

    @property
    def inconclusive(self) -> Iterable[Source]:
        return filter(lambda src: not src.is_identified, self.sources)

    def ingest(self, unidentifed: Source):
        self.update_equiv_src(unidentifed)
        self.update_equiv_src(unidentifed)

    def update_equiv_src(self, new_src: Source):
        """"If the new source is within the margin of an old source, add its audio to the old source and
        analyze with ML"""
        for src in self.sources:
            if src.position.within_margin(resonant.SOURCE_MARGIN, new_src.position):
                src.update_audio(new_src.audio)
                src.position = new_src.position

                # It only runs ml if it has enough samples to analyze
                if src.can_ml_analyze:
                    self.ml.analyze(src)

                    # This means the ML was conclusive and it keeps it alive
                    if src.name is not None:
                        src.reset_cycles()

                return
                
        # If there are no equivalent sources, add it to the tracked sources
        new_src.track()
        self.sources.append(new_src)

    def filter_srcs(self, new_src: Source):
        # Decrease cycles for all items in array and removes expired
        srcs_to_remove = []

        for src in self.sources:
            # Decreases life and removes sources if needed
            if src.can_ml_analyze:
                src.decrease_life()
                if src.is_expired:
                    self.sources.remove(src)
                    continue

                """if src.name == new_src.name:
                    # This most likely means it's the same source, so remove the new added source
                    # And increase life of old one
                    src.reset_cycles()
                    src.position = new_src.position
                elif src.name != new_src.name
                    # Case where old source wasn't identified but now is
                    src.identify_as(new_src.name)
                    src.reset_cycles()

                elif src.name is None:
                    if new_src.name is None:
                        # This means that no updates were made to the source and it should be removed
                        # If it has expired
                        if new_src.is_expired:
                            self.sources.remove(src)"""
