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
        )

        tests = setup.with_exec(
            ['coverage', 'run', '--source=thipster', '-m', 'pytest', 'tests/'],
        ).with_exec(['coveralls'])

        # execute
        await tests.sync()

    print('Tests succeeded!')


if __name__ == '__main__':
    python_version = '3.11.3'
    anyio.run(test, python_version)
