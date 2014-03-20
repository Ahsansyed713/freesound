# -*- coding: utf-8 -*-

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

from django.db import models
from django.contrib.auth.models import User

class FollowingUserItem(models.Model):
    user_from = models.ForeignKey(User, related_name='following_items')
    user_to = models.ForeignKey(User, related_name='follower_items')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s following %s" % (self.user_from, self.user_to)

    class Meta:
        verbose_name_plural = "Users"
        unique_together = ("user_from", "user_to")

class FollowingTagItem(models.Model):
    user = models.ForeignKey(User)
    query = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s following tag %s" % (self.user, self.query)

    class Meta:
        verbose_name_plural = 'Tags'
        unique_together = ("user", "query")
