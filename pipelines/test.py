import sys

import anyio
import base
import dagger


async def test(version: str):
    """Runs all the automated tests
    """
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        src = client.host().directory('.')

        setup = (
            base.thipsterBase(client, version)
            .with_mounted_directory('/src', src)
            .with_workdir('/src')
            .with_exec(['pip', 'install', '-e', '.[test]'])

        )

        tests = setup.with_exec(['pytest', 'tests'])
        # execute
        await tests.exit_code()

    print('Tests succeeded!')


if __name__ == '__main__':
    anyio.run(test, "3.11.3")
