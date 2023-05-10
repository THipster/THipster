import sys

import anyio
import base
import dagger


async def test():
    """Runs all the automated tests
    """
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        python = add_all_tests_step(base.pythonBase(client, '3.11'))

        # execute
        await python.exit_code()

    print('Tests succeeded!')


def add_all_tests_step(precedent_container: dagger.Container) -> dagger.Container:
    """Adds a step to a dagger pipeline container to run all the automated tests

    Parameters
    ----------
    precedent_container : Container
        The container to add the step to

    Returns
    -------
    Container
        Returns a container with the step to run all the automated tests
    """
    return (
        precedent_container
        # Install Terraform CDK
        .with_exec(['wget', 'https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['unzip', 'terraform_1.4.6_linux_amd64.zip'])
        .with_exec(['mv', 'terraform', '/usr/bin/terraform'])
        # Install NodeJS
        .with_exec(['apk', 'add', 'nodejs', 'npm'])
        # Install Python dependencies
        .with_exec(['pip', 'install', '-e', '.[test]'])
        .with_exec(['pytest', 'tests'])

    )


if __name__ == '__main__':
    anyio.run(test)
