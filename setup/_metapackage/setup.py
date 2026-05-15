import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-open-synergy-opnsynid-server-tools",
    description="Meta package for open-synergy-opnsynid-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-base_document_version',
        'odoo12-addon-base_qr_code',
        'odoo12-addon-base_sequence_configurator',
        'odoo12-addon-base_workflow_policy',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
