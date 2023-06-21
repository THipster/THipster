"""Pull request handler pipeline."""
import anyio
import precommit
from automated_tests import test


async def pr_handler(version):
    """Run the pre-commit and test pipelines in parallel."""
    async with anyio.create_task_group() as tg:
        tg.start_soon(precommit.pre_commit, version)
        tg.start_soon(test, version)

if __name__ == '__main__':
    versions = ['3.11.3']
    for version in versions:
        anyio.run(pr_handler, version)
