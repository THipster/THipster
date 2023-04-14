import sys

import anyio
import base
import dagger

async def test():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        python = (
            base.pythonBase(client, "3.11")
            .with_exec(["pip", "install", "-e", ".[test]"])
            .with_exec(["pytest", "tests"])
        )

        # execute
        await python.exit_code()

    print("Tests succeeded!")


if __name__ == "__main__":
    anyio.run(test)