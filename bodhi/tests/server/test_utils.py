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

from bodhi.server.buildsys import setup_buildsystem, teardown_buildsystem
from bodhi.server.config import config
from bodhi.server.util import (get_critpath_pkgs, get_nvr, markup,
                               get_rpm_header, cmd, sorted_builds)


class TestUtils(object):

    def setUp(self):
        setup_buildsystem({'buildsystem': 'dev'})

    def tearDown(self):
        teardown_buildsystem()

    def test_config(self):
        assert config.get('sqlalchemy.url'), config
        assert config['sqlalchemy.url'], config

    def test_get_critpath_pkgs(self):
        """Ensure the pkgdb's critpath API works"""
        pkgs = get_critpath_pkgs()
        assert 'kernel' in pkgs, pkgs

    def test_get_nvr(self):
        """Assert the correct return value and type from get_nvr()."""
        result = get_nvr(u'ejabberd-16.12-3.fc26')

        assert result == ('ejabberd', '16.12', '3.fc26')
        for element in result:
            assert isinstance(element, unicode)

    def test_markup(self):
        """Ensure we escape HTML"""
        text = '<b>bold</b>'
        html = markup(None, text)
        assert html == (
            "<div class='markdown'>"
            '<p>--RAW HTML NOT ALLOWED--bold--RAW HTML NOT ALLOWED--</p>'
            "</div>"
        ), html

    def test_rpm_header(self):
        h = get_rpm_header('')
        assert h['name'] == 'libseccomp', h

    def test_cmd_failure(self):
        try:
            cmd('false')
            assert False
        except Exception:
            pass

    def test_sorted_builds(self):
        new = 'bodhi-2.0-1.fc24'
        old = 'bodhi-1.5-4.fc24'
        b1, b2 = sorted_builds([new, old])
        assert b1 == new, b1
        assert b2 == old, b2
