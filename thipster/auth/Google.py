import google.auth
from thipster.engine.I_Auth import I_Auth
from cdktf_cdktf_provider_google.provider import GoogleProvider


class GoogleAuth(I_Auth):
    """Authentication to GCP Projects

    Methods
    -------
    authenticate(app: Construct)
        Generates the google provider in terraform

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
