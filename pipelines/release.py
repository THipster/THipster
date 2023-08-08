"""Release pipeline."""
import anyio
from automated_tests import test_coveralls

if __name__ == '__main__':
    versions = ['3.11.3']
    for version in versions:
        anyio.run(test_coveralls, version)
