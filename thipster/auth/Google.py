import json
import os
from thipster.engine.I_Auth import I_Auth
from cdktf_cdktf_provider_google.provider import GoogleProvider


class GoogleAuth(I_Auth):
    """Authentication to GCP Projects

    Methods
    -------
    authenticate(self: Construct)
        Generates the google provider in terraform

    """

    def __init__(self) -> None:
        return GoogleAuth

    def authenticate(self):
        credentials = os.getenv("GOOGLE_CREDENTIALS")

        if not credentials:
            print("-"*10, "Authentication", "-"*10)
            print("No authentication found in GOOGLE_CREDENTIALS")
            credentials = input("Relative path to credentials file : ")

        if not os.path.isfile(credentials):
            project = json.loads(credentials)["project_id"]
        else:
            with open(credentials) as f:
                project = json.loads(f.read())["project_id"]
                f.close()

        GoogleProvider(
            self, "default_google",
            project=project,
            credentials=credentials if not os.path.isfile(credentials)
            or os.path.isabs(credentials)
            else os.path.join(
                os.getcwd(),
                credentials,
            ),
        )
