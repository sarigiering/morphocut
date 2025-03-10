from morphocut.core import Pipeline, ReturnOutputs, Output
from morphocut.filters import (
    BinomialFilter,
    ExponentialSmoothingFilter,
    MaxFilter,
    MedianFilter,
    _WindowFilter,
)
from morphocut.stream import Unpack
import numpy as np
import pytest


@ReturnOutputs
@Output("response")
class IdFilter(_WindowFilter):
    def _update(self, value):
        return value


@pytest.mark.parametrize(
    "filter_cls", [MaxFilter, MedianFilter, BinomialFilter, IdFilter]
)
def test_filter_negative_size(filter_cls):
    values = list(range(10))
    with pytest.raises(ValueError, match="size must be positive"):
        with Pipeline() as p:
            value = Unpack(values)
            response = filter_cls(value, size=-1)


@pytest.mark.parametrize(
    "filter_cls", [MaxFilter, MedianFilter, BinomialFilter, IdFilter]
)
def test_filter_even_size_centered(filter_cls):
    values = list(range(10))
    with pytest.raises(ValueError, match="size must be odd if centered"):
        with Pipeline() as p:
            value = Unpack(values)
            response = filter_cls(value, size=4, centered=True)


def test_binomial_uncentered():
    values = list(range(10))
    with pytest.raises(
        ValueError, match="BinomialFilter only supports centered filters"
    ):
        with Pipeline() as p:
            value = Unpack(values)
            response = BinomialFilter(value, size=3, centered=False)


@pytest.mark.parametrize("centered", [True, False])
@pytest.mark.parametrize("filter_cls", [MaxFilter, MedianFilter, IdFilter])
def test_filter_scalar(filter_cls, centered):
    values = list(range(10))

    with Pipeline() as p:
        value = Unpack(values)
        response = filter_cls(value, size=5, centered=centered)

    responses = [obj[response] for obj in p.transform_stream()]

    assert len(responses) == len(values)


@pytest.mark.parametrize("filter_cls", [MaxFilter, MedianFilter, BinomialFilter])
def test_filter_scalar_centered_is_symmetric(filter_cls):
    size = 5

    values = list(range(10))
    values_r = values[::-1]

    with Pipeline() as p:
        value, value_r = Unpack(zip(values, values_r)).unpack(2)

        response = filter_cls(value, size=size, centered=True)
        response_r = filter_cls(value_r, size=size, centered=True)

    objs = list(p.transform_stream())
    responses = [obj[response] for obj in objs]
    responses_r = [obj[response_r] for obj in objs]

    print(responses)

    assert responses == responses_r[::-1]


@pytest.mark.parametrize("shape", [(), (1,), (4, 6), (4, 6, 3)])
@pytest.mark.parametrize("filter_cls", [MaxFilter, MedianFilter, BinomialFilter])
def test_filter_numpy(filter_cls, shape):
    values = [i * np.ones(shape) for i in range(20)]

    with Pipeline() as p:
        value = Unpack(values)
        response = filter_cls(value, size=3)

    responses = [obj[response] for obj in p.transform_stream()]

    print(values)
    print(responses)

    assert len(responses) == len(values)

    for resp in responses:
        assert resp.shape == shape


def test_ExponentialSmoothingFilter():
    with Pipeline() as p:
        value = Unpack(range(20))
        running_median = ExponentialSmoothingFilter(value, 0.5)

    p.run()
