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
            app, "default_google",
            project=project_id,
            access_token=credentials.token,
        )
