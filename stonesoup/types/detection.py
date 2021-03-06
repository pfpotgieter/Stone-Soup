# -*- coding: utf-8 -*-
from typing import MutableMapping

from .groundtruth import GroundTruthPath
from .state import CategoricalState
from .state import State, GaussianState, StateVector
from ..base import Property
from ..models.measurement import MeasurementModel


class Detection(State):
    """Detection type"""
    measurement_model: MeasurementModel = Property(
        default=None,
        doc="The measurement model used to generate the detection (the default is ``None``)")

    metadata: MutableMapping = Property(
        default=None, doc='Dictionary of metadata items for Detections.')

    def __init__(self, state_vector, *args, **kwargs):
        super().__init__(state_vector, *args, **kwargs)
        if self.metadata is None:
            self.metadata = {}


class GaussianDetection(Detection, GaussianState):
    """GaussianDetection type"""


class Clutter(Detection):
    """Clutter type for detections classed as clutter

    This is same as :class:`~.Detection`, but can be used to identify clutter
    for metrics and analysis purposes.
    """


class TrueDetection(Detection):
    """TrueDetection type for detections that come from ground truth

    This is same as :class:`~.Detection`, but can be used to identify true
    detections for metrics and analysis purposes.
    """

    groundtruth_path: GroundTruthPath = Property(
        doc="Ground truth path that this detection came from")


class MissedDetection(Detection):
    """Detection type for a missed detection

    This is same as :class:`~.Detection`, but it is used in
    MultipleHypothesis to indicate the null hypothesis (no
    detections are associated with the specified track).
    """

    state_vector: StateVector = Property(default=None, doc="State vector. Default `None`.")

    def __init__(self, state_vector=None, *args, **kwargs):
        super().__init__(state_vector, *args, **kwargs)

    def __bool__(self):
        return False


class CategoricalDetection(Detection, CategoricalState):
    """Categorical detection type."""


class TrueCategoricalDetection(TrueDetection, CategoricalDetection):
    """TrueCategoricalDetection type for categorical detections that come from ground truth."""
