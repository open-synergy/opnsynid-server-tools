import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-opnsynid-server-tools",
    description="Meta package for open-synergy-opnsynid-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-base_workflow_policy',
        'odoo11-addon-webhook',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
