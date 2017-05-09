#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     See AUTHORS file.
#

from django.core.management.base import BaseCommand
from similarity.client import Similarity
from optparse import make_option
import logging
logger = logging.getLogger("web")


class Command(BaseCommand):
    args = ''
    help = 'Save current similarity index'
    def add_arguments(self, parser):
        parser.add_argument(
            '-i','--indexing_server',
            action='store_true',
            dest='indexing_server',
            default=False,
            help='Save the index of the indexing server instead of the index of the main similarity server')

    def handle(self, *args, **options):
        logger.info('Saving current similarity index')

        if options['indexing_server']:
            Similarity.save_indexing_server()
        else:
            Similarity.save()

