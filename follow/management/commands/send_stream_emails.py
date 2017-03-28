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
from utils.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings
from utils.mail import render_mail_template
from accounts.models import Profile, EmailPreferenceType
import datetime
from follow import follow_utils
from django.contrib.auth.models import User
import logging
logger = logging.getLogger("web")


class Command(BaseCommand):
    """
    This command should be run periodically several times a day, and it will only send emails to users that "require it"
    """
    help = 'Send stream notifications to users who have not been notified for the last ' \
           'settings.NOTIFICATION_TIMEDELTA_PERIOD period and whose stream has new sounds for that period'
    args = True  # For backwards compatimility mdoe
    # See: http://stackoverflow.com/questions/30244288/django-management-command-cannot-see-arguments

    def handle(self, *args, **options):

        date_today_minus_notification_timedelta = datetime.datetime.now() - settings.NOTIFICATION_TIMEDELTA_PERIOD

        # Get all the users that have notifications active
        # and exclude the ones that have the last email sent for less than settings.NOTIFICATION_TIMEDELTA_PERIOD
        # (because they have been sent an email already)
        email_type = EmailPreferenceType.objects.get(name="stream_email")
        user_ids = email_type.users_set.values('id')

        users_enabled_notifications = Profile.objects.filter(user_id__in=user_ids).exclude(
            last_stream_email_sent__gt=date_today_minus_notification_timedelta).order_by(
            "-last_attempt_of_sending_stream_email")[:settings.MAX_EMAILS_PER_COMMAND_RUN]

        logger.info("Sending stream updates notification for %i potential users" % len(users_enabled_notifications))

        email_tuples = ()
        n_emails_sent = 0
        for profile in users_enabled_notifications:

            username = profile.user.username
            email_to = profile.user.email
            profile.last_attempt_of_sending_stream_email = datetime.datetime.now()

            # Variable names use the terminology "week" because settings.NOTIFICATION_TIMEDELTA_PERIOD defaults to a
            # week, but a more generic terminology could be used
            week_first_day = profile.last_stream_email_sent
            week_last_day = datetime.datetime.now()

            week_first_day_str = week_first_day.strftime("%d %b").lstrip("0")
            week_last_day_str = week_last_day.strftime("%d %b").lstrip("0")

            subject_str = u'new sounds from users and tags you are following ('
            subject_str += unicode(week_first_day_str) + u' - ' + unicode(week_last_day_str) + u')'

            # Set date range from which to get upload notifications
            time_lapse = follow_utils.build_time_lapse(week_first_day, week_last_day)

            # construct message
            user = User.objects.get(username=username)
            try:
                users_sounds, tags_sounds = follow_utils.get_stream_sounds(user, time_lapse)
            except Exception, e:
                # If error occur do not send the email
                print "could not get new sounds data for", username.encode('utf-8')
                profile.save()  # Save last_attempt_of_sending_stream_email
                continue

            if not users_sounds and not tags_sounds:
                print "no news sounds for", username.encode('utf-8')
                profile.save()  # Save last_attempt_of_sending_stream_email
                continue

            text_content = render_mail_template('follow/email_stream.txt', locals())
            email_tuples += (subject_str, text_content, settings.DEFAULT_FROM_EMAIL, [email_to]),

            # Send email
            try:
                send_mail(subject_str, text_content, email_from=settings.DEFAULT_FROM_EMAIL, email_to=[email_to],
                          reply_to=None)
            except Exception, e:
                logger.info("An error occurred sending notification stream email to %s (%s)" % (str(email_to), str(e)))
                # Do not send the email and do not update the last email sent field in the profile
                profile.save()  # Save last_attempt_of_sending_stream_email
                continue
            n_emails_sent += 1

            # update last stream email sent date
            profile.last_stream_email_sent = datetime.datetime.now()
            profile.save()

        logger.info("Sent stream updates notification to %i users (others had no updates)" % n_emails_sent)
