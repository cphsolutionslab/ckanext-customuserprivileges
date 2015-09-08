"""Tests for plugin.py."""
import mock
import nose
import ckan.tests.helpers as helpers
import pylons.test

import ckan.tests.factories as factories
import ckan.model as model
import ckan.logic as logic
import ckan.tests.legacy as tests
import ckan.plugins
import ckanext.customuserprivileges.plugin as plugin

class TestCustomUserPrivileges(object):
    '''
    Tests for the ckanext.customuserprivileges.plugin module.
    '''

    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''

        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        ckan.plugins.load('customuserprivileges')

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''

        # Rebuild CKAN's database after each test method, so that each test
        # method runs with a clean slate.
        model.repo.rebuild_db()

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.
        '''

        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        ckan.plugins.unload('customuserprivileges')

    def test_unowned_only_creator_can_edit(self):
        fred = factories.User(name='fred')
        bob = factories.User(name='bob')
        dataset = factories.Dataset(user=fred)
        context = {'model': model, 'user': 'fred'}
        params = {
             'id': dataset['id'],
         }
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        #Bob should not be able to edit package
        context = {'model': model, 'user': 'bob'}
        nose.tools.assert_raises(logic.NotAuthorized, helpers.call_auth, 'package_update', context=context, **params)

    def test_unowned_only_managing_users_can_edit(self):
        fred = factories.User(name='fred')
        bob = factories.User(name='bob')
        alice = factories.User(name='alice')
        lisa = factories.User(name='lisa')
        dataset = factories.Dataset(user=fred, managing_users='bob,alice')
        context = {'model': model, 'user': 'fred'}
        params = {
             'id': dataset['id'],
         }
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        #Bob and alice should be also able to edit
        context = {'model': model, 'user': 'bob'}
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        context = {'model': model, 'user': 'alice'}
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        #Lisa shuldn't be able
        context = {'model': model, 'user': 'lisa'}
        nose.tools.assert_raises(logic.NotAuthorized, helpers.call_auth, 'package_update', context=context, **params)

    def test_owned_dataset_company_users_should_edit(self):
        org = factories.Organization()
        fred = factories.User(name='fred')
        bob = factories.User(name='bob')
        alice = factories.User(name='alice')

        member_fred = {'username': fred['name'],
                  'role': 'admin',
                  'id': org['id']}
        helpers.call_action('organization_member_create', **member_fred)

        member_bob = {'username': bob['name'],
                  'role': 'admin',
                  'id': org['id']}
        helpers.call_action('organization_member_create', **member_bob)

        dataset = factories.Dataset(user=fred, owner_org=org['name'])
        context = {'model': model, 'user': 'fred'}
        params = {
             'id': dataset['id'],
         }
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        context = {'model': model, 'user': 'bob'}
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        #Alice is not in the organization
        context = {'model': model, 'user': 'alice'}
        nose.tools.assert_raises(logic.NotAuthorized, helpers.call_auth, 'package_update', context=context, **params)


    def test_owned_dataset_with_admins_company_users_should_not_edit(self):
        org = factories.Organization()
        fred = factories.User(name='fred')
        bob = factories.User(name='bob')
        alice = factories.User(name='alice')

        member_fred = {'username': fred['name'],
                  'role': 'admin',
                  'id': org['id']}
        helpers.call_action('organization_member_create', **member_fred)

        member_bob = {'username': bob['name'],
                  'role': 'admin',
                  'id': org['id']}
        helpers.call_action('organization_member_create', **member_bob)

        dataset = factories.Dataset(user=fred, owner_org=org['name'], managing_users="someone")
        context = {'model': model, 'user': 'fred'}
        params = {
             'id': dataset['id'],
         }
        result = helpers.call_auth('package_update', context=context, **params)
        assert result == True
        context = {'model': model, 'user': 'bob'}
        nose.tools.assert_raises(logic.NotAuthorized, helpers.call_auth, 'package_update', context=context, **params)
        assert result == True
        #Alice is not in the organization
        context = {'model': model, 'user': 'alice'}
        nose.tools.assert_raises(logic.NotAuthorized, helpers.call_auth, 'package_update', context=context, **params)
