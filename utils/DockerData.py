import docker
class DockerData:
    class __DockerData:
        imgs = {
            'python':'python:3.7.5-slim',
            'r':'rocker/r-ver:3.6.2',
        }
        CLIENT = None
        CONTAINERS = None
        VOLUME = None
        PATH_FILES = "/builds/shared/SourceCloze/compiler/"
        PATH_FILES_DOCKER = "/home/SourceCloze/"
        def __init__(self):
            self.CLIENT = self.init_client()
            self.init_container(self.CLIENT)

        def init_client(self):
            client = docker.from_env()
            if len(client.images.list(name=self.imgs['python'])) == 0:
                client.images.pull(self.imgs['python'])
            if len(client.images.list(name=self.imgs['r'])) == 0:
                client.images.pull(self.imgs['r'])
            return client
        
        def init_container(self, client):
            self.VOLUME = self.fetch_volume(client)
            self.CONTAINERS = self.fetch_containers(client, 
                {self.PATH_FILES: {'bind': self.PATH_FILES_DOCKER, 'mode': 'rw'}})

        def fetch_volume(self, client):
            try:
                return client.volumes.get('SC_Volume')
            except docker.errors.NotFound as e:
                try:
                    return client.volumes.create(name='SC_Volume', driver='local',
                        driver_opts={'device': self.PATH_FILES, 'o':'bind'}
                        # ,labels={"key": "value"}
                        )
                except docker.errors.NotFound as e1:
                    print('cannot create volume SC_Volume')
                    raise e1
        def fetch_containers(self, client, volumes):
            # print("containers0: ", client.containers.list(all=True))
            for c in client.containers.list(all=True):
                print(c, c.id, c.image, c.name, c.short_id, c.status)
                if (c.name in ["SC_container_py", "SC_container_r"]):
                    print('remove: ', c.name)
                    c.stop()
                    c.remove(force=True)
                    continue
            # print("containers1: ", client.containers.list(all=True))
            containers = {
                'python': client.containers.run(self.imgs['python'],  
                    command=['/bin/bash'], 
                    tty=True, detach=True, working_dir="/", 
                    volume_driver='local', volumes=volumes),
                'r': client.containers.run(self.imgs['r'], 
                    command=['/bin/bash'],
                    tty=True, detach=True, working_dir="/", 
                    volume_driver='local', volumes=volumes),
            }
            containers['python'].rename("SC_container_py")
            containers['r'].rename("SC_container_r")
            print("containers: ", client.containers.list(all=True))
            return containers
        def status(self, lang):
            return self.CONTAINERS[lang].status

        def __str__(self):
            return repr(self) + self.val
    instance = None
    def __init__(self):
        if not DockerData.instance:
            DockerData.instance = DockerData.__DockerData()
    def __getattr__(self, name):
        return getattr(self.instance, name)

    def get_container(self, lang):
        if DockerData.instance.status(lang) != 'created':
            DockerData.instance.CONTAINERS = DockerData.instance.init_containers(DockerData.instance.CLIENT)
        return DockerData.instance.CONTAINERS[lang]
