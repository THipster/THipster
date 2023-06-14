import test

import anyio
import precommit


async def pr_handler(version):
    async with anyio.create_task_group() as tg:
        tg.start_soon(precommit.pre_commit, version)
        tg.start_soon(test.test, version)

if __name__ == '__main__':
    versions = ['3.11.3']
    for version in versions:
        anyio.run(pr_handler, version)
