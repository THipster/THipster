"""Step that runs automated tests in a pipeline."""
import os
import sys

import anyio
import base
import dagger


async def test(version: str):
    """Run all the automated tests."""
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        gcp_credentials_content = (
            client.set_secret(
                'GOOGLE_APPLICATION_CREDENTIALS_CONTENT',
                os.environ['GOOGLE_APPLICATION_CREDENTIALS_CONTENT'],
            )
        )

        coveralls_token = (
            client.set_secret(
                'COVERALLS_REPO_TOKEN',
                os.environ['COVERALLS_REPO_TOKEN'],
            )
        )

        src = client.host().directory('.')

        setup = (
            base.thipster_base(client, version)
            .with_mounted_directory('/src', src)
            .with_workdir('/src')
            .with_exec(['pip', 'install', '-e', '.[test]'])
            .with_secret_variable(
                'GOOGLE_APPLICATION_CREDENTIALS_CONTENT', gcp_credentials_content,
            )
            .with_secret_variable('COVERALLS_REPO_TOKEN', coveralls_token)
            .with_(
                env_variables(
                    [
                        'CI_NAME',
                        'CI_BUILD_NUMBER',
                        'CI_BRANCH',
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


def env_variables(env_keys: list[str]):
    """Add specified environment variables to a container if defined."""
    def env_variables_inner(ctr: dagger.Container):
        for key in env_keys:
            if key in os.environ:
                ctr = ctr.with_env_variable(key, os.environ[key])
        return ctr

    return env_variables_inner


def get_active_branch_name():
    """Get the name of the active git branch."""
    from pathlib import Path
    return Path('.git/HEAD').read_text().split('/')[-1].strip()


if __name__ == '__main__':
    python_version = '3.11.3'
    os.environ['CI_NAME'] = 'dagger local'
    os.environ['CI_BRANCH'] = get_active_branch_name()
    anyio.run(test, python_version)
