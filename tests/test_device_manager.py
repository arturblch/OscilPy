import pytest
from src.DeviceManager import DeviceManager
from tests.fake_log import Fake_log


def test_init():
    dm = DeviceManager(Fake_log())

def test_add_device():
    dm = DeviceManager(Fake_log())
    dm.add_device('123')