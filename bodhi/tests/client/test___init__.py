# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""This module contains tests for bodhi.client."""
import datetime
import os
import platform
import unittest

from click import testing
import fedora.client
import mock

from bodhi import client
from bodhi.client import bindings
from bodhi.tests import client as client_test_data


EXPECTED_DEFAULT_BASE_URL = os.environ.get('BODHI_URL', bindings.BASE_URL)


class TestComment(unittest.TestCase):
    """
    Test the comment() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_COMMENT_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.comment,
            ['nodejs-grunt-wrap-0.3.0-2.fc25', 'After installing this I found $100.', '--user',
             'bowlofeggs', '--password', 's3kr3t', '--url', 'http://localhost:6543', '--karma',
             '1'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, client_test_data.EXPECTED_COMMENT_OUTPUT)
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'comments/', verb='POST', auth=True,
            data={'csrf_token': 'a_csrf_token', 'text': 'After installing this I found $100.',
                  'update': u'nodejs-grunt-wrap-0.3.0-2.fc25', 'email': None, 'karma': 1})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestDownload(unittest.TestCase):
    """
    Test the download() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_QUERY_MUNCH, autospec=True)
    @mock.patch('bodhi.client.subprocess.call', return_value=0)
    def test_url_flag(self, call, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.download,
            ['--builds', 'nodejs-grunt-wrap-0.3.0-2.fc25', '--url', 'http://localhost:6543'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output,
                         'Downloading packages from nodejs-grunt-wrap-0.3.0-2.fc25\n')
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'updates/', verb='GET',
            params={'builds': u'nodejs-grunt-wrap-0.3.0-2.fc25'})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')
        call.assert_called_once_with((
            'koji', 'download-build', '--arch=noarch', '--arch={}'.format(platform.machine()),
            'nodejs-grunt-wrap-0.3.0-2.fc25'))


class TestNew(unittest.TestCase):
    """
    Test the new() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_UPDATE_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.new,
            ['--user', 'bowlofeggs', '--password', 's3kr3t', 'bodhi-2.2.4-1.el7',
             '--url', 'http://localhost:6543'])

        self.assertEqual(result.exit_code, 0)
        expected_output = client_test_data.EXPECTED_UPDATE_OUTPUT.replace('example.com/tests',
                                                                          'localhost:6543')
        self.assertEqual(result.output, expected_output + '\n')
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'updates/', auth=True, verb='POST',
            data={
                'close_bugs': True, 'stable_karma': None, 'csrf_token': 'a_csrf_token',
                'staging': False, 'builds': u'bodhi-2.2.4-1.el7', 'autokarma': True,
                'suggest': None, 'notes': None, 'request': None, 'bugs': u'',
                'unstable_karma': None, 'file': None, 'notes_file': None, 'type': 'bugfix'})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestQuery(unittest.TestCase):
    """
    Test the query() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_UPDATE_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.query,
            ['--builds', 'nodejs-grunt-wrap-0.3.0-2.fc25', '--url', 'http://localhost:6543'])

        self.assertEqual(result.exit_code, 0)
        self.maxDiff = 2000
        expected_output = client_test_data.EXPECTED_UPDATE_OUTPUT.replace('example.com/tests',
                                                                          'localhost:6543')
        self.assertEqual(result.output, expected_output + '\n')
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'updates/', verb='GET',
            params={
                'approved_since': None, 'status': None, 'locked': None,
                'builds': u'nodejs-grunt-wrap-0.3.0-2.fc25', 'releases': None,
                'submitted_since': None, 'suggest': None, 'request': None, 'bugs': None,
                'staging': False, 'modified_since': None, 'pushed': None, 'pushed_since': None,
                'user': None, 'critpath': None, 'updateid': None, 'packages': None, 'type': None,
                'cves': None})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestQueryBuildrootOverrides(unittest.TestCase):
    """
    This class tests the query_buildroot_overrides() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_QUERY_OVERRIDES_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.query_buildroot_overrides,
            ['--user', 'bowlofeggs', '--url', 'http://localhost:6543'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, client_test_data.EXPECTED_QUERY_OVERRIDES_OUTPUT)
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'overrides/', verb='GET',
            params={'user': u'bowlofeggs'})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestRequest(unittest.TestCase):
    """
    This class tests the request() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.__init__', return_value=None)
    @mock.patch.object(client.bindings.BodhiClient, 'base_url', 'http://example.com/tests/',
                       create=True)
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_UPDATE_MUNCH)
    def test_successful_operation(self, send_request, __init__):
        """
        Assert that a successful operation is handled properly.
        """
        runner = testing.CliRunner()

        result = runner.invoke(client.request, ['bodhi-2.2.4-1.el7', 'revoke', '--user',
                                                'some_user', '--password', 's3kr3t'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, client_test_data.EXPECTED_UPDATE_OUTPUT + '\n')
        send_request.assert_called_once_with(
            'updates/bodhi-2.2.4-1.el7/request', verb='POST', auth=True,
            data={'csrf_token': 'a_csrf_token', 'request': u'revoke',
                  'update': u'bodhi-2.2.4-1.el7'})
        __init__.assert_called_once_with(base_url=EXPECTED_DEFAULT_BASE_URL, username='some_user',
                                         password='s3kr3t', staging=False)

    @mock.patch('bodhi.client.bindings.BodhiClient.__init__', return_value=None)
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                side_effect=fedora.client.ServerError(
                    url='http://example.com/tests/updates/bodhi-2.2.4-99.el7/request', status=404,
                    msg='update not found'))
    def test_update_not_found(self, send_request, __init__):
        """
        Assert that request() transforms a bodhi.client.bindings.UpdateNotFound into a
        click.BadParameter so that the user gets a nice error message.
        """
        runner = testing.CliRunner()

        result = runner.invoke(client.request, ['bodhi-2.2.4-99.el7', 'revoke', '--user',
                                                'some_user', '--password', 's3kr3t'])

        self.assertEqual(result.exit_code, 2)
        self.assertEqual(
            result.output,
            (u'Usage: request [OPTIONS] UPDATE STATE\n\nError: Invalid value for UPDATE: Update not'
             u' found: bodhi-2.2.4-99.el7\n'))
        send_request.assert_called_once_with(
            'updates/bodhi-2.2.4-99.el7/request', verb='POST', auth=True,
            data={'csrf_token': 'a_csrf_token', 'request': u'revoke',
                  'update': u'bodhi-2.2.4-99.el7'})
        __init__.assert_called_once_with(base_url=EXPECTED_DEFAULT_BASE_URL, username='some_user',
                                         password='s3kr3t', staging=False)

    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_UPDATE_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.request,
            ['bodhi-2.2.4-99.el7', 'revoke', '--user', 'some_user', '--password', 's3kr3t', '--url',
             'http://localhost:6543'])

        self.assertEqual(result.exit_code, 0)
        expected_output = client_test_data.EXPECTED_UPDATE_OUTPUT.replace('example.com/tests',
                                                                          'localhost:6543')
        self.assertEqual(result.output, expected_output + '\n')
        bindings_client = send_request.mock_calls[0][1][0]
        send_request.assert_called_once_with(
            bindings_client, 'updates/bodhi-2.2.4-99.el7/request', verb='POST', auth=True,
            data={'csrf_token': 'a_csrf_token', 'request': u'revoke',
                  'update': u'bodhi-2.2.4-99.el7'})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestSaveBuilrootOverrides(unittest.TestCase):
    """
    Test the save_buildroot_overrides() function.
    """
    @mock.patch('bodhi.client.bindings.BodhiClient.csrf',
                mock.MagicMock(return_value='a_csrf_token'))
    @mock.patch('bodhi.client.bindings.BodhiClient.send_request',
                return_value=client_test_data.EXAMPLE_OVERRIDE_MUNCH, autospec=True)
    def test_url_flag(self, send_request):
        """
        Assert correct behavior with the --url flag.
        """
        runner = testing.CliRunner()

        result = runner.invoke(
            client.save_buildroot_overrides,
            ['--user', 'bowlofeggs', '--password', 's3kr3t', 'js-tag-it-2.0-1.fc25', '--url',
             'http://localhost:6543/'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            result.output,
            "bowlofeggs's js-tag-it-2.0-1.fc25 override (expires 2017-03-07 23:05:31)\n")
        bindings_client = send_request.mock_calls[0][1][0]
        # datetime is a C extension that can't be mocked, so let's just assert that the time is
        # about a week away.
        expire_time = send_request.mock_calls[0][2]['data']['expiration_date']
        self.assertTrue((datetime.datetime.utcnow() - expire_time) < datetime.timedelta(seconds=5))
        send_request.assert_called_once_with(
            bindings_client, 'overrides/', verb='POST', auth=True,
            data={
                'expiration_date': expire_time,
                'notes': u'No explanation given...', 'nvr': u'js-tag-it-2.0-1.fc25',
                'csrf_token': 'a_csrf_token'})
        self.assertEqual(bindings_client.base_url, 'http://localhost:6543/')


class TestWarnIfUrlAndStagingSet(unittest.TestCase):
    """
    This class tests the _warn_if_url_and_staging_set() function.
    """
    @mock.patch('bodhi.client.click.echo')
    def test_staging_false(self, echo):
        """
        Nothing should be printed when staging is False.
        """
        ctx = mock.MagicMock()
        ctx.params = {'staging': False}

        result = client._warn_if_url_and_staging_set(ctx, mock.MagicMock(),
                                                     'http://localhost:6543')

        self.assertEqual(result, 'http://localhost:6543')
        self.assertEqual(echo.call_count, 0)

    @mock.patch('bodhi.client.click.echo')
    def test_staging_missing(self, echo):
        """
        Nothing should be printed when staging is not present in the context.
        """
        ctx = mock.MagicMock()
        ctx.params = {}

        result = client._warn_if_url_and_staging_set(ctx, mock.MagicMock(),
                                                     'http://localhost:6543')

        self.assertEqual(result, 'http://localhost:6543')
        self.assertEqual(echo.call_count, 0)

    @mock.patch('bodhi.client.click.echo')
    def test_staging_true(self, echo):
        """
        A warning should be printed to stderr when staging is True.
        """
        ctx = mock.MagicMock()
        ctx.params = {'staging': True}

        result = client._warn_if_url_and_staging_set(ctx, mock.MagicMock(),
                                                     'http://localhost:6543')

        self.assertEqual(result, 'http://localhost:6543')
        echo.assert_called_once_with(
            '\nWarning: url and staging flags are both set. url will be ignored.\n', err=True)
