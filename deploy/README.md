# Optional AWS deployment

The deploy workflow is manually triggered. Configure the GitHub `aws` environment with `AWS_REGION`, `AWS_DEPLOY_ROLE`, `ECR_REPOSITORY`, `REVISION_BUCKET`, `CODEDEPLOY_APP`, and `CODEDEPLOY_GROUP`. Restrict the IAM role trust to the intended repository and environment using GitHub's OIDC subject and audience.

- **CI role** requires ECR authorization, upload and describe permissions scoped to the application repository where supported, S3 PutObject scoped to the revision prefix, and CodeDeploy create/read access scoped where supported.
- **EC2 instance role** needs ECR read access and S3 read access to deployment revisions and any private model artifact prefix. Use a separate CodeDeploy service role.
- **EC2** needs Docker Engine, AWS CLI, curl, the CodeDeploy agent and the three local model outputs under `/opt/spotify-data`. Provision matching artifacts from a private, versioned S3 prefix when deploying to multiple instances. Leave public access blocked on the S3 buckets.
- **Release** uses an ECR digest and an S3 revision key per workflow attempt. CodeDeploy calls the hooks in `appspec.yml`. The start hook checks Streamlit's health endpoint.
- **Networking** requires a route to the AWS APIs. For public use, restrict instance ingress to a load balancer and terminate HTTPS there.

AWS credentials and resources are optional for the Windows and Compose paths. Cloud rollout and IAM policy validation require an AWS environment.
