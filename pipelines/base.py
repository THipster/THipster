import dagger


def pythonBase(client: dagger.Client, version: str) -> dagger.Container:
    """Returns a dagger pipeline container with the python base image

    Parameters
    ----------
    client : dagger.Client
        The dagger client instance
    version : str
        The desired python version

    Returns
    -------
    Container
        Returns a container with the python base image
    """

    src = client.host().directory('.')

    python = (
        client.container()
        .from_(f'python:{version}-alpine')
        .with_mounted_directory('/src', src)
        .with_workdir('/src')
        .with_exec(['apk', 'upgrade', '--no-cache'])
        .with_exec(['pip', 'install', '-e', '.'])
    )

    return python
