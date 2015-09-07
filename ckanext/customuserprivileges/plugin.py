import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.customuserprivileges.logic.auth.update import managing_users_package_update

class CustomuserprivilegesPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IDatasetForm)

    # IAuthFunctions
    def get_auth_functions(self):
        return {
                'package_update': managing_users_package_update
                }

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customuserprivileges')

    # IDatasetForm
    def create_package_schema(self):
        schema = super(CustomuserprivilegesPlugin, self).create_package_schema()
        schema.update({
            'managing_users': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
                ]
        })
        return schema

    def update_package_schema(self):
        schema = super(CustomuserprivilegesPlugin, self).update_package_schema()
        schema.update({
            'managing_users': [toolkit.get_validator('ignore_missing'),
                            toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(CustomuserprivilegesPlugin, self).show_package_schema()
        schema.update({
            'managing_users': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
