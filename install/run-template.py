from typing import Any, Dict, List


# GENERATE_RANDOM_TOKEN_COMMAND = "head -c '500' '/dev/urandom'" \
#                                 " | tr -dc 'a-zA-Z0-9'" \
#                                 " | fold -w '33'" \
#                                 " | head -n '1'"
#
# CREATE_TOKEN_STDIN_COMMAND_TEMPLATE = "gcloud secrets create " \
#                                       "'{deployment}-token' " \
#                                       "--data-file='-' " \
#                                       "--labels='app={deployment}' " \
#                                       "--replication-policy='automatic' " \
#                                       "--project='{project}'"
#
# CREATE_TOKEN_COMMAND_TEMPLATE = ' | '.join([GENERATE_RANDOM_TOKEN_COMMAND, CREATE_TOKEN_STDIN_COMMAND_TEMPLATE])
#
# DELETE_TOKEN_COMMAND_TEMPLATE = "gcloud secrets delete " \
#                                 "'{deployment}-token' " \
#                                 "--project='{project}'"
#
# GRANT_ROLE_COMMAND_TEMPLATE = "gcloud secrets add-iam-policy-binding " \
#                               "'{deployment}-token' " \
#                               "--member='serviceAccount:{deployment}-proxy@{project}.iam.gserviceaccount.com' " \
#                               "--role='roles/secretmanager.secretAccessor' " \
#                               "--project='{project}'"
INTERNAL_PYPI_GCS_PROXY_IMAGE_SUFFIX = 'pypi-gcs-proxy:latest'
PYPI_GCS_PROXY_IMAGE = 'backupner/pypi-gcs-proxy:latest'


def generate_config(context: Any) -> Dict[str, List]:
    """We use `Cloud Build` actions here because of related `gcp-types` are not available for `Run` now.

    Todo: create custom type providers (or wait for Google)"""
    deployment = context.env['deployment']
    project = context.env['project']
    image_name_template = 'eu.gcr.io/{project}/{INTERNAL_PYPI_GCS_PROXY_IMAGE_SUFFIX}'
    internal_pypi_gcs_proxy_image = image_name_template.format(project=project, INTERNAL_PYPI_GCS_PROXY_IMAGE_SUFFIX=INTERNAL_PYPI_GCS_PROXY_IMAGE_SUFFIX)
    # create_token_command = CREATE_TOKEN_COMMAND_TEMPLATE.format(deployment=deployment, project=project)
    # delete_token_command = DELETE_TOKEN_COMMAND_TEMPLATE.format(deployment=deployment, project=project)
    # grant_role_command = GRANT_ROLE_COMMAND_TEMPLATE.format(deployment=deployment, project=project)
    resources = [
        {
            'name': 'download-{deployment}-proxy-container-image'.format(deployment=deployment),
            'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
            'metadata': {
                'runtimePolicy': ['CREATE'],
            },
            'properties': {
                'steps': [
                    {
                        'name': 'gcr.io/cloud-builders/docker',
                        'args': ['pull', PYPI_GCS_PROXY_IMAGE],
                    },
                    {
                        'name': 'gcr.io/cloud-builders/docker',
                        'args': ['tag', PYPI_GCS_PROXY_IMAGE, internal_pypi_gcs_proxy_image],
                    },
                    {
                        'name': 'gcr.io/cloud-builders/docker',
                        'args': ['push', internal_pypi_gcs_proxy_image],
                    },
                ],
                'timeout': '120s',
                'options': {
                    'env': [
                        'CLOUDSDK_CORE_DISABLE_PROMPTS=1',
                    ],
                    'sourceProvenanceHash': ['SHA256'],
                },
                'tags': [deployment],
                'images': [
                    internal_pypi_gcs_proxy_image,
                ],
            },
        },
        # {
        #     'name': 'deploy-{deployment}-proxy-run-container'.format(deployment=deployment),
        #     'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
        #     'metadata': {
        #         'dependsOn': [
        #             'download-{deployment}-proxy-container-image'.format(deployment=deployment),
        #         ],
        #         'runtimePolicy': ['CREATE'],
        #     },
        #     'properties': {
        #         'steps': [
        #             # {
        #             #     'name': 'gcr.io/cloud-builders/gcloud',
        #             #     'entrypoint': 'bash',
        #             #     'args': [
        #             #         '-c',
        #             #         create_token_command,
        #             #     ],
        #             # },
        #             # {
        #             #     'name': 'gcr.io/cloud-builders/gcloud',
        #             #     'entrypoint': 'bash',
        #             #     'args': [
        #             #         '-c',
        #             #         grant_role_command,
        #             #     ],
        #             # },
        #         ],
        #         'timeout': '120s',
        #         'options': {
        #             'env': [
        #                 'CLOUDSDK_CORE_DISABLE_PROMPTS=1',
        #             ],
        #         },
        #         'tags': [deployment],
        #     },
        # },
        # {
        #     'name': 'delete-{deployment}-proxy-run-service'.format(deployment=deployment),
        #     'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
        #     'metadata': {
        #         'runtimePolicy': ['DELETE'],
        #     },
        #     'properties': {
        #         'steps': [
        #             # {
        #             #     'name': 'gcr.io/cloud-builders/gcloud',
        #             #     'entrypoint': 'bash',
        #             #     'args': [
        #             #         '-c',
        #             #         delete_token_command,
        #             #     ],
        #             #     'env': [
        #             #         'CLOUDSDK_CORE_DISABLE_PROMPTS=1',
        #             #     ],
        #             # },
        #         ],
        #         'timeout': '120s',
        #         'options': {
        #             'env': [
        #                 'CLOUDSDK_CORE_DISABLE_PROMPTS=1',
        #             ],
        #         },
        #         'tags': [deployment],
        #     },
        # },
    ]
    return {
        'resources': resources,
    }
