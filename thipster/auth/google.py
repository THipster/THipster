import google.auth
from cdktf_cdktf_provider_google.provider import GoogleProvider

from thipster.engine import I_Auth


class GoogleAuth(I_Auth):
    """Authentication to GCP Projects
    """

    def __init__(self) -> None:
        return GoogleAuth

    def authenticate(app):
        """Generates the google provider block for the Terraform CDK

        Parameters
        ----------
        app: Construct
            CDK Construct where the provider is created

        """

        credentials, project_id = google.auth.default()

        GoogleProvider(
            app, 'default_google',
            project=project_id,
            access_token=credentials.token,
        )

    @property
    def description(self) -> str:
        """Description of this authentification module

        Returns
        -------
        str
            Description of the class

        """
        return "Authenticate to Google Cloud Platform (GCP) projects"

    @property
    def help(self) -> str:
        """Detailed help to use this authentification module

        Returns
        -------
        str
            Help on the usage of the authentificate methode contained in the class

        """
        return """
To use this module, you need to have a GCP account and a project created. 
You also need to have gcloud installed : https://cloud.google.com/sdk/docs/install
Then login using glcloud : gcloud auth application-default login
"""
