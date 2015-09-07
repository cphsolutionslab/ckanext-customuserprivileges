import ckan.logic.auth as logic_auth
import ckan.authz as authz
from ckan.common import _
# FIXME this import is evil and should be refactored
from ckan.logic.auth.create import _check_group_auth

def managing_users_package_update(context, data_dict):
    user = context.get('user')
    package = logic_auth.get_package_object(context, data_dict)
    extras = dict([(key, value) for key, value in package.extras.items()])

    if package.owner_org:
        # if there is an owner org then we must have update_dataset
        # permission for that organization
        check1 = authz.has_user_permission_for_group_or_org(
            package.owner_org, user, 'update_dataset'
        )
        #If managing users are specified within the organization, only them can edit it
        #Else only creator can edit the dataset
        if 'managing_users' in extras and extras['managing_users'] != '':
            managing_users = extras.get('managing_users', '')
            managing_users = managing_users.split(',')
            check1 = check1 and context['auth_user_obj'].name in managing_users
    else:
        # If dataset is not owned then we can edit if config permissions allow
        if authz.auth_is_anon_user(context):
            check1 = all(authz.check_config_permission(p) for p in (
                'anon_create_dataset',
                'create_dataset_if_not_in_organization',
                'create_unowned_dataset',
                ))
        else:
            check1 = all(authz.check_config_permission(p) for p in (
                'create_dataset_if_not_in_organization',
                'create_unowned_dataset',
                )) or authz.has_user_permission_for_some_org(
                user, 'create_dataset')
            #Managing users have to be specified for datasets without owner
            #Else only creator can edit the dataset
            managing_users = extras.get('managing_users', '')
            managing_users = managing_users.split(',')
            check1 = check1 and context['auth_user_obj'].name in managing_users

    
    if context['auth_user_obj'].id == package.creator_user_id:
        #If user is the creator of the package, he can edit it regardless
        check1 = True
    if not check1:
        return {'success': False,
                'msg': _('User %s not authorized to edit package %s') %
                        (str(user), package.id)}
    else:
        check2 = _check_group_auth(context, data_dict)
        if not check2:
            return {'success': False,
                    'msg': _('User %s not authorized to edit these groups') %
                            (str(user))}

    return {'success': True}
