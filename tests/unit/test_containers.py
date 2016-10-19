"""Test container classes"""
from dockerff.containers import BaseContainer


def test_parse_container_config_correct():
    container_config = {
        'ports': ['80:8080'],
        'volumes': ['/host/dir:/docker/dir']
    }
    pc = BaseContainer.parse_container_config(container_config)
    assert pc['port_bindings'] == {'80': '8080'}
    assert pc['ports'] == ['80']
    assert pc['volumes'] == ['/docker/dir']
    assert pc['binds'] == {'/host/dir': '/docker/dir'}


def test_parse_container_config_empty():
    container_config = {
        'ports': [],
        'volumes': []
    }
    pc = BaseContainer.parse_container_config(container_config)
    assert pc['port_bindings'] == {}
    assert pc['ports'] == []
    assert pc['volumes'] == []
    assert pc['binds'] == {}
