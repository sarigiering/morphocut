from morphocut import Node, Pipeline, Output, ReturnOutputs, LambdaNode
import pytest


@ReturnOutputs
class TestNodeNoTransform(Node):
    pass


@ReturnOutputs
@Output("a")
@Output("b")
@Output("c")
class TestNode(Node):
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

    def transform(self, a, b, c):
        return a, b, c


def test_Node():
    # Assert that Node checks for the existence of a pipeline
    with pytest.raises(RuntimeError):
        TestNode(1, 2, 3)

    # Assert that Node checks for the existance of transform
    with Pipeline() as pipeline:
        TestNodeNoTransform()

    with pytest.raises(AttributeError):
        pipeline.run()

    # Assert that parameters and outputs are passed as expected
    with Pipeline() as pipeline:
        a, b, c = TestNode(1, 2, 3)

    obj, *_ = list(pipeline.transform_stream())
    assert obj[a] == 1
    assert obj[b] == 2
    assert obj[c] == 3


def test_LambdaNode():
    def foo(bar, baz):
        return bar, baz

    with Pipeline() as pipeline:
        result = LambdaNode(foo, 1, 2)

    obj, *_ = list(pipeline.transform_stream())
    assert obj[result] == (1, 2)
