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

import math

from cornice import Service
from pyramid.exceptions import HTTPNotFound
from sqlalchemy.sql import or_

from bodhi import log
from bodhi.models import Update, Build, Package, Release
import bodhi.schemas
import bodhi.security
from bodhi.validators import (
    validate_nvrs,
    validate_version,
    validate_uniqueness,
    validate_tags,
    validate_acls,
    validate_builds,
    validate_enums,
    validate_updates,
    validate_packages,
    validate_releases,
    validate_release,
    validate_username,
    validate_groups,
)


release = Service(name='release', path='/releases/{name}',
                  description='Fedora Releases')
releases = Service(name='releases', path='/releases/',
                   description='Fedora Releases')


@release.get(renderer='json')
def get_release(request):
    id = request.matchdict.get('name')
    release = Release.get(id, request.db)
    if not release:
        request.errors.add('body', 'name', 'No such release')
        request.errors.status = HTTPNotFound.code
    return release


@releases.get(schema=bodhi.schemas.ListReleaseSchema, renderer='json',
              validators=(validate_release, validate_updates,
                          validate_packages))
def query_releases(request):
    db = request.db
    data = request.validated
    query = db.query(Release)

    name = data.get('name')
    if name is not None:
        query = query.filter(Release.name.like(name))

    updates = data.get('updates')
    if updates is not None:
        query = query.join(Release.builds).join(Build.update)
        args = \
            [Update.title == update.title for update in updates] +\
            [Update.alias == update.alias for update in updates]
        query = query.filter(or_(*args))

    packages = data.get('packages')
    if packages is not None:
        query = query.join(Release.builds).join(Build.package)
        query = query.filter(or_(*[Package.id == p.id for p in packages]))

    total = query.count()

    page = data.get('page')
    rows_per_page = data.get('rows_per_page')
    pages = int(math.ceil(total / float(rows_per_page)))
    query = query.offset(rows_per_page * (page - 1)).limit(rows_per_page)

    return dict(releases=query.all())
