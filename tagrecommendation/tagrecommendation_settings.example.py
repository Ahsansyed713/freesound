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

import os
# NOTE: In production and test this file is taken from the deploy repository

# SERVER SETTINGS
LOGFILE                     = '/var/log/freesound/tagrecommendation.log'
LISTEN_PORT                 = 8010
RECOMMENDATION_DATA_DIR     = '/home/fsweb/freesound/freesound-tagrecommendation/'
RECOMMENDATION_TMP_DATA_DIR = RECOMMENDATION_DATA_DIR + 'tmp/'

# CLIENT SETTINGS (to be moved to django settings?)
TAGRECOMMENDATION_ADDRESS          = 'localhost'
TAGRECOMMENDATION_PORT             = 8010
TAGRECOMMENDATION_CACHE_TIME       = 60*60*24*7 # One week?


# This tag recommendation server needs some data files to be in the data folder
#
# For the class detection step:
#   Classifier.pkl              (precomputed classifier pickled)
#   Classifier_meta.json        (metadata of the classifier)
#   Classifier_TAG_NAMES.npy    (vector of all tag names used to train the classifier)
#
# Classifier files can be found in freesound-deploy repository.
#
# Having this classifier the recommendation server can be started. Once the server is running
# a command from the appservers must be run so the recomendation is feeded with tag assignement data
# from freesound which is stored in a file called Index.json. This fille incrementally stores
# all tag assingment information from freesound. Once this file exists and has some data, the
# "update_tagrecommendation_data.py" script can be run and will generate the following files:
#
# For every class used:
#   [[DATABASE]]_[[CLASSNAME]]_SIMILARITY_MATRIX_cosine_SUBSET.npy
#   [[DATABASE]]_[[CLASSNAME]]_SIMILARITY_MATRIX_cosine_SUBSET_TAG_NAMES.npy
# Example:
#   FREESOUND2012_CFX_SIMILARITY_MATRIX_cosine_SUBSET.npy
#   FREESOUND2012_CFX_SIMILARITY_MATRIX_cosine_SUBSET_TAG_NAMES.npy
#   ...
#
# Once the files are generated the recommendation service is restarted and ready.