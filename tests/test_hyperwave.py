
from hyperwave import Hyperwave

def test_should_return_2():
    hw = Hyperwave()

    assert 1 == hw.get_value()


def test_should_return_val():
    hw = Hyperwave()
    val = 4
    assert val - 1 == hw.get_value(val)
