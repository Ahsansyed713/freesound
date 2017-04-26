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
import base64
import requests
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from sounds.models import Sound
import gearman
import tickets.views

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/')
def monitor_home(request):
    sounds_in_moderators_queue_count =\
        tickets.views._get_sounds_in_moderators_queue_count(request.user)

    new_upload_count = tickets.views.new_sound_tickets_count()
    tardy_moderator_sounds_count =\
        len(tickets.views._get_tardy_moderator_tickets())

    tardy_user_sounds_count = len(tickets.views._get_tardy_user_tickets())

    # Processing
    sounds_queued_count = Sound.objects.filter(
            processing_ongoing_state='QU').count()
    sounds_pending_count = Sound.objects.\
        filter(processing_state='PE')\
        .exclude(processing_ongoing_state='PR')\
        .exclude(processing_ongoing_state='QU')\
        .count()
    sounds_processing_count = Sound.objects.filter(
            processing_ongoing_state='PR').count()
    sounds_failed_count = Sound.objects.filter(
            processing_state='FA').count()
    sounds_ok_count = Sound.objects.filter(
            processing_state='OK').count()

    # Analysis
    sounds_analysis_pending_count = Sound.objects.filter(
        analysis_state='PE').count()
    sounds_analysis_queued_count = Sound.objects.filter(
        analysis_state='QU').count()
    sounds_analysis_ok_count = Sound.objects.filter(
        analysis_state='OK').count()
    sounds_analysis_failed_count = Sound.objects.filter(
        analysis_state='FA').count()
    sounds_analysis_skipped_count = Sound.objects.filter(
        analysis_state='SK').count()

    # Get gearman status
    try:
        gm_admin_client = gearman.GearmanAdminClient(settings.GEARMAN_JOB_SERVERS)
        gearman_status = gm_admin_client.get_status()
    except gearman.errors.ServerUnavailable:
        gearman_status = list()

    tvars = {"new_upload_count": new_upload_count,
             "tardy_moderator_sounds_count": tardy_moderator_sounds_count,
             "tardy_user_sounds_count": tardy_user_sounds_count,
             "sounds_queued_count": sounds_queued_count,
             "sounds_pending_count": sounds_pending_count,
             "sounds_processing_count": sounds_processing_count,
             "sounds_failed_count": sounds_failed_count,
             "sounds_ok_count": sounds_ok_count,
             "sounds_analysis_pending_count": sounds_analysis_pending_count,
             "sounds_analysis_queued_count": sounds_analysis_queued_count,
             "sounds_analysis_ok_count": sounds_analysis_ok_count,
             "sounds_analysis_failed_count": sounds_analysis_failed_count,
             "sounds_analysis_skipped_count": sounds_analysis_skipped_count,
             "gearman_status": gearman_status,
             "sounds_in_moderators_queue_count": sounds_in_moderators_queue_count
    }

    return render(request, 'monitor/monitor.html', tvars)


def queries_stats_ajax(request):
    try:
        auth = (settings.GRAYLOG_USERNAME, settings.GRAYLOG_PASSWORD)
        params = {
            'query': '*',
            'range': 14 * 60 * 60 * 24,
            'filter': 'streams:%s' % settings.GRAYLOG_SEARCH_STREAM_ID,
            'field': 'query'
        }
        req = requests.get(settings.GRAYLOG_DOMAIN + '/graylog/api/search/universal/relative/terms',
                auth=auth, params=params)
        return JsonResponse(req.json())
    except requests.HTTPError:
        return HttpResponse(status=500)


@login_required
def api_usage_stats_ajax(request, client_id):
    try:
        auth = (settings.GRAYLOG_USERNAME, settings.GRAYLOG_PASSWORD)
        params = {
            'query': 'api_client_id:%s' % (client_id),
            'range': 14 * 60 * 60 * 24,
            'filter': 'streams:%s' % settings.GRAYLOG_API_STREAM_ID,
            'interval': 'day'
        }
        req = requests.get(settings.GRAYLOG_DOMAIN + '/graylog/api/search/universal/relative/histogram',
                auth=auth, params=params)
        return JsonResponse(req.json())
    except requests.HTTPError:
        return HttpResponse(status=500)


def tags_stats_ajax(request):
    tags_stats = cache.get("tags_stats")
    return JsonResponse(tags_stats or {})


def sounds_stats_ajax(request):
    sounds_stats = cache.get("sounds_stats")
    return JsonResponse(sounds_stats or {})


def active_users_stats_ajax(request):
    active_users_stats = cache.get("active_users_stats")
    return JsonResponse(active_users_stats or {})


def users_stats_ajax(request):
    users_stats = cache.get("users_stats")
    return JsonResponse(users_stats or {})


def downloads_stats_ajax(request):
    downloads_stats = cache.get("downloads_stats")
    return JsonResponse(downloads_stats or {})


def donations_stats_ajax(request):
    donations_stats = cache.get("donations_stats")
    return JsonResponse(donations_stats or {})


def totals_stats_ajax(request):
    totals_stats = cache.get("totals_stats")
    return JsonResponse(totals_stats or {})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/')
def process_sounds(request):

    # Send sounds to processing according to their processing_state
    processing_status = request.GET.get('prs', None)
    if processing_status:
        sounds_to_process = None
        if processing_status in ['FA', 'PE']:
            sounds_to_process = Sound.objects.filter(processing_state=processing_status)

        # Remove sounds from the list that are already in the queue or are being processed right now
        if sounds_to_process:
            sounds_to_process = sounds_to_process.exclude(processing_ongoing_state='PR')\
                .exclude(processing_ongoing_state='QU')
            for sound in sounds_to_process:
                sound.process()

    # Send sounds to processing according to their processing_ongoing_state
    processing_ongoing_state = request.GET.get('pros', None)
    if processing_ongoing_state:
        sounds_to_process = None
        if processing_ongoing_state in ['QU', 'PR']:
            sounds_to_process = Sound.objects.filter(processing_ongoing_state=processing_ongoing_state)

        if sounds_to_process:
            for sound in sounds_to_process:
                sound.process()

    # Send sounds to analysis according to their analysis_state
    analysis_state = request.GET.get('ans', None)
    if analysis_state:
        sounds_to_analyze = None
        if analysis_state in ['QU', 'PE', 'FA', 'SK']:
            sounds_to_analyze = Sound.objects.filter(analysis_state=analysis_state)

        if sounds_to_analyze:
            for sound in sounds_to_analyze:
                sound.process()

    return redirect("monitor-home")
