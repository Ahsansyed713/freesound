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
from oauth2_provider.models import AbstractApplication, Application
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site


class ExtendedApplication(AbstractApplication):
    redirect_uri_scheme = models.CharField(max_length=100, default=None)

    def get_allowed_schemes(self):
        schemes = super(ExtendedApplication, self).get_allowed_schemes()
        if self.redirect_uri_scheme is not None:
            return schemes + [self.redirect_uri_scheme]
        return schemes


class ApiV2Client(models.Model):

    STATUS_CHOICES = (('OK',  'Approved'),
                      ('REJ', 'Rejected'),
                      ('REV', 'Revoked'),
                      ('PEN', 'Pending'))

    DEFAULT_STATUS = 'OK'

    oauth_client = models.OneToOneField(ExtendedApplication, related_name='apiv2_client', default=None, null=True, blank=True)
    key = models.CharField(max_length=40, blank=True)
    user = models.ForeignKey(User, related_name='apiv2_client')
    status = models.CharField(max_length=3, default=DEFAULT_STATUS, choices=STATUS_CHOICES)
    name = models.CharField(max_length=64)
    url = models.URLField()
    redirect_uri = models.URLField()
    description = models.TextField(blank=True)
    accepted_tos = models.BooleanField(default=False)
    allow_oauth_passoword_grant = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    throttling_level = models.IntegerField(default=1)

    def __unicode__(self):
        return "credentials for developer %s" % self.user.username

    def save(self, *args, **kwargs):

        # If oauth client does not exist create a new one (that means ApiV2Client is being saved for the first time)
        # Otherwise update existing client

        # If redirect_uri has not been set, use Freesound redirect uri by default
        if not self.redirect_uri:
            redirect_uri_base = "https://%s%s"
            if settings.DEBUG:
                redirect_uri_base = "http://%s%s"
            self.redirect_uri = redirect_uri_base % (Site.objects.get_current().domain, reverse('permission-granted'))

        if not self.oauth_client:
            # Set oauth client (create oauth client object)
            oauth_client = ExtendedApplication.objects.create(
                user=self.user,
                name=self.name,
                redirect_uris=self.redirect_uri,
                client_type=ExtendedApplication.CLIENT_PUBLIC,
                authorization_grant_type=ExtendedApplication.GRANT_AUTHORIZATION_CODE,
            )
            self.oauth_client = oauth_client

            # Set key (using same key as in oauth client to simplify work for developers)
            self.key = self.oauth_client.client_secret

        else:
            # Update existing oauth client
            self.oauth_client.name = self.name
            self.oauth_client.redirect_uris = self.redirect_uri
            self.oauth_client.save()

        return super(ApiV2Client, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # On delete, delete also oauth client
        self.oauth_client.delete()
        super(ApiV2Client, self).delete(*args, **kwargs)
    
    @property
    def client_id(self):
        return self.oauth_client.client_id

    @property
    def client_secret(self):
        return self.oauth_client.client_secret
    
    @property
    def version(self):
        return "V2"
