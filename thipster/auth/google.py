"""Google Cloud Platform (GCP) authentication module."""
import google.auth
from cdktf_cdktf_provider_google.provider import GoogleProvider

from thipster.engine import AuthPort


class GoogleAuth(AuthPort):
    """Authenticate to Google Cloud Platform (GCP) projects.

    To use this module, you need to have a GCP account and a project created.
    You also need to have gcloud installed : https://cloud.google.com/sdk/docs/install
    Then login using glcloud : gcloud auth application-default login
    """

    @classmethod
    def authenticate(cls, app):
        """Generate the google provider block for the Terraform CDK.

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
