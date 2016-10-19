"""
Common interface for the containers
"""
import logging
from operator import itemgetter

from docker import Client as DockerClient
from docker.utils import LogConfig

from dockerff.settings import FLUENTD_IMAGE, FIREFOX_IMAGE, DOCKERFF_PREFIX

logger = logging.getLogger('containers')


class BaseContainer(object):
    """Base operations over container.

    Class attributes:

    :ivar mark: container mark (the uniq id associated with container (0, 1...)
    :ivar name: tag name for the container
    :ivar image: docker image string
    :ivar docker: docker client instance
    :ivar container_id: docker id associated with this container
    :ivar container_status: current container status
    :ivar container_info: low level information about container
    :ivar _container_config: container config like volumes and ports mapping

    Container config example:

    >> _container_config = {
    >>     'ports': ['4444:None']  # autoassign host port
    >>     'volumes': ['/host/dir:/container/dir']  # map host volume to the
    >>                                               # container
    >> }

    Possible container statuses:

    >> [
    >>     'initializing', 'initialized',
    >>     'starting', 'started',
    >>     'working', 'fatal',
    >>     'stopping', 'stopped'
    >> ]
    """

    mark = None
    name = '{}_base'.format(DOCKERFF_PREFIX)
    image = 'busybox'

    docker = None
    fluentd_logs_dir = None
    container_id = None
    container_status = None
    container_info = None

    _container_config = {
        'ports': [],
        'volumes': [],
    }

    def __init__(self, image=None,
                 container_config=None):
        """ Create base container instance

        :param image: image for the container
        :type image: string or None (default: `busybox`)
        :param container_config: ports/volumes configuration
        :type container_config: dict or None
        """
        if image:
            self.image = image
        if container_config:
            self._container_config.update(container_config)

        self.docker = DockerClient()
        self.container_id = self.init()
        self.container_info = self.docker.inspect_container(self.container_id)

    def start(self):
        self.container_status = 'starting'
        self.docker.start(self.container_id)
        self.container_info = self.docker.inspect_container(self.container_id)
        self.container_status = 'started'

    def stop(self):
        self.container_status = 'stopping'
        self.docker.stop(self.container_id)
        self.container_info = self.docker.inspect_container(self.container_id)
        self.docker.remove_container(self.container_id)
        self.container_id = None
        self.container_status = 'stopped'

    def init(self):
        if self.container_id:
            logger.debug(
                "Container {} already initialized".format(self.container_id))
            return self.container_id

        self.container_status = 'initializing'
        # parse container configuration and map parsed
        # values to the docker api
        container_config = self.parse_container_config(self._container_config)
        host_config = self.docker.create_host_config(
            port_bindings=container_config['port_bindings'],
            binds=container_config['binds']
        )

        container = self.docker.create_container(
            self.image, detach=True,
            ports=container_config['ports'],
            volumes=container_config['volumes'],
            host_config=host_config
        )
        self.container_status = 'initialized'
        return container.get('Id')

    @classmethod
    def parse_container_config(cls, container_config):
        # parse ports
        parsed_ports = []
        ports = container_config['ports']
        for port in ports:
            cont_port, host_port = port.split(':')
            if host_port == 'None':
                host_port = None
            parsed_ports.append((cont_port, host_port))
        # parse volumes
        parsed_volumes = []
        volumes = container_config['volumes']
        for volume in volumes:
            host_volume, cont_volume = volume.split(':')
            parsed_volumes.append((host_volume, cont_volume))
        return {
            'ports': list(map(itemgetter(0), parsed_ports)),
            'port_bindings': dict(parsed_ports),
            'volumes': list(map(itemgetter(1), parsed_volumes)),
            'binds': dict(parsed_volumes),
        }

    def __str__(self):
        return "<Container: {} Name: {} Id: '{}'>".format(
            self.__class__.__name__, self.name, self.container_id)


class FluentdContainer(BaseContainer):
    """ Fluentd docker container manager
    """

    name = '{}_fluentd'.format(DOCKERFF_PREFIX)
    image = FLUENTD_IMAGE

    def init(self, path):
        _container = self.docker.create_container(
            self.image, detach=True,
            ports=[24224], volumes=[self.fluentd_logs_dir],
            host_config=self.docker_cli.create_host_config(
                port_bindings={
                    24224: 24224,
                },
                binds=[
                    '{}:{}'.format(
                        path,
                        self.fluentd_logs_dir),
                ]
            )
        )
        return _container.get('Id')


class FirefoxStandaloneContainer(BaseContainer):
    """Firefox docker container manager
    """

    name = '{}_firefox'.format(DOCKERFF_PREFIX)
    image = FIREFOX_IMAGE
