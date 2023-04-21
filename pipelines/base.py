import dagger


def pythonBase(client: dagger.Client, version: str):
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
