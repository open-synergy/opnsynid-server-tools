import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-opnsynid-server-tools",
    description="Meta package for open-synergy-opnsynid-server-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_copy_user_access',
        'odoo14-addon-base_custom_system_parameter',
        'odoo14-addon-base_duration',
        'odoo14-addon-base_public_holiday',
        'odoo14-addon-base_user_copy_user_role',
        'odoo14-addon-base_user_role_menu',
        'odoo14-addon-ssi_frequency',
        'odoo14-addon-test_base_duration',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
