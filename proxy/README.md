Proxy
=====

This service adds basic auth with tokens support and provides access to packages. Simple layer between Storage and end users.

Implementation
--------------

- managed Google Cloud Run
  - uses Python image with Starlette Python ASGI framework (it should be fast)
- uses Google Cloud Secret Manager for auth tokens storage

Setup
-----

### Manual

#### Build image

Run Cloud Build process:
`$ gcloud builds submit --config proxy/images/pypi-gcs-proxy/cloudbuild.yaml proxy/images/pypi-gcs-proxy --project=YOUR_PROJECT_ID`.

#### Create Service Account. Add permissions

...

#### Create Secret

...

#### Run service

Use Google Cloud Run to run this image. 

Set required environment variables. 

Check logs on errors. You may need activate several APIs.

#### Configure custom domain name

...

### Automatic

Use Cloud Deployment Manager (https://cloud.google.com/deployment-manager/) and/or Terraform. Please, open new PR, contribute your code.
