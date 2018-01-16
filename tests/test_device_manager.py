import pytest
import src.DeviceManager
import Fake_log


def test_init():
    dm = DeviceManager(Fake_log())

def test_add_device():
    dm = DeviceManager(Fake_log())
    dm.add_device('123')