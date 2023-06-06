"""Dedicated module for Terraform-related actions.

This module contains all the code linked to Terraform, including the
generation of the Terraform CDK constructs and the creation of the
Terraform code itself.
It also allows user to execute Terraform commands from the THipster package.
"""

from .cdk import CDK as Terraform
