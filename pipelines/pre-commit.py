import sys

import anyio
import base
import dagger

async def pre_commit():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        python = (
            base.pythonBase(client, "3.11")
            .with_exec(["apk", "add", "git", "libgcc"])
            .with_exec(["git", "config", "--global", "safe.directory", "*"])
            .with_exec(["git", "add",".pre-commit-config.yaml"])
            .with_exec(["pip", "install", "pre-commit"])
            .with_exec(["pre-commit"])
        )

        # execute
        await python.exit_code()

    print("Pre-commit passed")

    
if __name__ == "__main__":
    anyio.run(pre_commit)