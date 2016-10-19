import os
import pytest
from dockerff.containers import BaseContainer


@pytest.fixture(scope="module")
def container():
    bc = BaseContainer()
    yield bc
    if bc.container_status != 'stopped':
        bc.stop()


@pytest.mark.skipif(os.environ.get("TRAVIS", None) == "true",
                    'Skipping Travis...')
def test_container_init():
    bc = BaseContainer()
    assert bc.container_id is not None
    assert bc.container_status == 'initialized'
    assert bc.init() == bc.container_id


@pytest.mark.skipif(os.environ.get("TRAVIS", None) == "true",
                    'Skipping Travis...')
def test_container_start_stop(container):
    container.start()
    assert container.container_id is not None
    assert container.container_status == 'started'
