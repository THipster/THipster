"""Step that runs automated tests in a pipeline."""
import os
import sys

import anyio
import base
import dagger


async def test(version: str):
    """Run all the automated tests."""
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        tests = base_tests_container(client, version).with_exec(
            ['coverage', 'run', '--source=thipster', '-m', 'pytest', 'tests/'],
        )

        # execute
        await tests.sync()

    print('Tests succeeded!')


async def test_coveralls(version: str):
    """Run all the automated tests with coverage upload to coveralls."""
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        coveralls_token = (
            client.set_secret(
                'COVERALLS_REPO_TOKEN',
                os.environ['COVERALLS_REPO_TOKEN'],
            )
        )

        setup = (
            base_tests_container(client, version)
            .with_secret_variable('COVERALLS_REPO_TOKEN', coveralls_token)
            .with_(
                env_variables(
                    [
                        'CI_NAME',
                        'CI_BUILD_NUMBER',
                        'CI_BUILD_URL',
                        'CI_BRANCH',
                        'CI_JOB_ID',
                        'CI_PULL_REQUEST',
                    ],
                ),
            )
        )

        tests = setup.with_exec(
            ['coverage', 'run', '--source=thipster', '-m', 'pytest', 'tests/'],
        ).with_exec(['coveralls'])

        # execute
        await tests.sync()

    print('Tests succeeded!')


def base_tests_container(client: dagger.Client, version: str) -> dagger.Container:
    """Return a base container to run thipster's tests."""
    gcp_credentials_content = (
        client.set_secret(
            'GOOGLE_APPLICATION_CREDENTIALS_CONTENT',
            os.environ['GOOGLE_APPLICATION_CREDENTIALS_CONTENT'],
        )
    )

    src = client.host().directory('.')

    return (
        base.thipster_base(client, version)
        .with_mounted_directory('/src', src)
        .with_workdir('/src')
        .with_exec(['pip', 'install', '-e', '.[test]'])
        .with_secret_variable(
            'GOOGLE_APPLICATION_CREDENTIALS_CONTENT', gcp_credentials_content,
        )
    )


def env_variables(env_keys: list[str]):
    """Add specified environment variables to a container if defined."""
    def env_variables_inner(ctr: dagger.Container) -> dagger.Container:
        for key in env_keys:
            if key in os.environ:
                ctr = ctr.with_env_variable(key, os.environ[key])
        return ctr

    return env_variables_inner


if __name__ == '__main__':
    python_version = '3.11.3'
    anyio.run(test, python_version)
