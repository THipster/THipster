import sys

import anyio
import base
import dagger


async def pre_commit(version: str):
    """Runs pre-commit on all project files
    """
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        src = client.host().directory('.')

        setup = (
            base.pythonBase(client, version)
            .with_exec(['apk', 'add', 'git', 'libgcc'])
            .with_exec(['git', 'config', '--global', 'safe.directory', '*'])
            .with_exec(['pip', 'install', 'pre-commit'])
            .with_mounted_directory('/src', src)
            .with_workdir('/src')
            .with_exec(['git', 'add', '.pre-commit-config.yaml'])
        )

        pre_commit = setup.with_exec(['pre-commit', 'run', '--all-files'])

        # execute
        await pre_commit.exit_code()

    print('Pre-commit passed')


if __name__ == '__main__':
    python_version = '3.11.3'
    anyio.run(pre_commit, python_version)
