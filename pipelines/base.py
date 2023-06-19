"""Base containers for the CI pipeline."""
import dagger


def python_base(client: dagger.Client, version: str) -> dagger.Container:
    """Return a dagger pipeline container with the python base image.

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
    return (
        client.container()
        .from_(f'python:{version}-alpine3.18')
        .with_exec(['apk', 'upgrade', '--no-cache'])
    )


def thipster_base(client: dagger.Client, version: str) -> dagger.Container:
    """Return a dagger pipeline container with the python base image for thipster.

    Parameters
    ----------
    client : dagger.Client
        The dagger client instance
    version : str
        The desired python version

    Returns
    -------
    Container
        Returns a container with all thipster dependencies, including nodejs and
        terraform
    """
    src = client.host().directory('.')
    requirements = 'requirements.txt'

    return (
        python_base(client, version)
        # Install Terraform CLI
        .with_exec(['wget', 'https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['unzip', 'terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['mv', 'terraform', '/usr/bin/terraform'])
        # Install NodeJS
        .with_exec(['apk', 'add', 'nodejs', 'npm'])
        # Install THipster dependencies
        .with_file(requirements, src.file(requirements))
        .with_exec(['pip', 'install', '-r', requirements])
    )
