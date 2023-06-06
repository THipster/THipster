"""Provider authentication module.

Allows users to authenticate themselves to the desired supported cloud provider.
Currently, only Google Cloud Platform is available.
"""

from .google import GoogleAuth as Google
