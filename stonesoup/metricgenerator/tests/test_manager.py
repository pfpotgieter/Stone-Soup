import datetime
import numpy as np

from ..manager import SimpleManager
from ..base import MetricGenerator
from ...dataassociator import Associator
from ...types.association import Association
from ...types.detection import Detection
from ...types.groundtruth import GroundTruthPath
from ...types.metric import Metric
from ...types.state import State
from ...types.track import Track


def test_adddata():
    manager = SimpleManager([])

    # Check adding data to empty manager
    tracks = [Track(
        states=State(np.array([[1]]), timestamp=datetime.datetime.now()))]
    truths = [GroundTruthPath(
        states=State(np.array([[2]]), timestamp=datetime.datetime.now()))]
    dets = [Detection(np.array([[3]]), timestamp=datetime.datetime.now())]

    manager.add_data(truths, tracks, dets)

    assert manager.tracks == set(tracks)
    assert manager.groundtruth_paths == set(truths)
    assert manager.detections == set(dets)

    # Check not overwriting data (flag is true by default)

    tracks2 = [Track(
        states=State(np.array([[21]]), timestamp=datetime.datetime.now()))]
    truths2 = [GroundTruthPath(
        states=State(np.array([[22]]), timestamp=datetime.datetime.now()))]
    dets2 = [Detection(np.array([[23]]), timestamp=datetime.datetime.now())]

    manager.add_data(truths2, tracks2, dets2, overwrite=False)

    assert manager.tracks == set(tracks + tracks2)
    assert manager.groundtruth_paths == set(truths + truths2)
    assert manager.detections == set(dets + dets2)

    # Check adding additional data including repeated data
    manager = SimpleManager([])
    manager.add_data(truths, tracks, dets)
    manager.add_data(truths + truths2, tracks + tracks2, dets + dets2, overwrite=True)

    assert manager.tracks == set(tracks2 + tracks)
    assert manager.groundtruth_paths == set(truths2 + truths)
    assert manager.detections == set(dets2 + dets)


def test_associate_tracks():
    class DummyAssociator(Associator):

        def associate_tracks(self, tracks, truths):

            associations = set()
            for track in tracks:
                for truth in truths:
                    associations.add(Association({track, truth}))
            return associations

    manager = SimpleManager(associator=DummyAssociator(), generators=[])
    tracks = {Track(
        states=State(np.array([[1]]), timestamp=datetime.datetime.now()))}
    truths = {GroundTruthPath(
        states=State(np.array([[2]]), timestamp=datetime.datetime.now()))}
    manager.add_data(truths, tracks)

    manager.associate_tracks()

    assert manager.association_set.pop().objects == tracks | truths


def test_listtimestamps():
    timestamp1 = datetime.datetime.now()
    timestamp2 = timestamp1 + datetime.timedelta(seconds=10)
    manager = SimpleManager(generators=[])
    tracks = [Track(
        states=[State(np.array([[1]]), timestamp=timestamp1)])]
    truths = [GroundTruthPath(
        states=[State(np.array([[2]]), timestamp=timestamp2)])]
    manager.add_data(truths, tracks)

    assert manager.list_timestamps() == [timestamp1, timestamp2]


def test_generate_metrics():
    class DummyGenerator1(MetricGenerator):

        def compute_metric(self, manager, *args, **kwargs):
            return Metric(title="Test metric1",
                          value=25,
                          generator=self)

    class DummyGenerator2(MetricGenerator):

        def compute_metric(self, manager, *args, **kwargs):
            return Metric(title="Test metric2 at times",
                          value=50,
                          generator=self)

    generator1 = DummyGenerator1()
    generator2 = DummyGenerator2()

    manager = SimpleManager(generators=[generator1, generator2])

    metrics = manager.generate_metrics()
    metric1 = [metrics.get(i) for i in metrics if metrics[i].generator == generator1][0]
    metric2 = [metrics.get(i) for i in metrics if metrics[i].generator == generator2][0]

    assert len(metrics) == 2
    assert metric1.title == "Test metric1"
    assert metrics.get("Test metric1") == metric1
    assert np.array_equal(metric1.value, 25)
    assert np.array_equal(metric1.generator, generator1)
    assert metric2.title == "Test metric2 at times"
    assert metrics.get("Test metric2 at times") == metric2
    assert np.array_equal(metric2.value, 50)
    assert np.array_equal(metric2.generator, generator2)
