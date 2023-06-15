import dagger


def python_base(client: dagger.Client, version: str) -> dagger.Container:
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

    python = (
        client.container()
        .from_(f'python:{version}-alpine3.18')
        .with_exec(['apk', 'upgrade', '--no-cache'])
    )

    return python


def thipster_base(client: dagger.Client, version: str) -> dagger.Container:
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
        Returns a container with all thipster dependencies
    """
    src = client.host().directory('.')

    thips = (
        python_base(client, version)
        # Install Terraform CLI
        .with_exec(['wget', 'https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['unzip', 'terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['mv', 'terraform', '/usr/bin/terraform'])
        # Install NodeJS
        .with_exec(['apk', 'add', 'nodejs', 'npm'])
        # Install THipster dependencies
        .with_file('requirements.txt', src.file('requirements.txt'))
        .with_exec(['pip', 'install', '-r', 'requirements.txt'])
    )
    return thips
