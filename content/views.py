import re
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, ListCreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from content.models import * 
from content.serializers import *
from django.db.models import Q
# mvt Imports
from django.shortcuts import render, redirect
from content.forms import CreateMovieForm

from django.conf import settings
import logging
from datetime import timedelta, timezone, datetime
import pytz
# from google.auth.transport import requests
from typing import Optional
from django.middleware.csrf import get_token
from django.http import JsonResponse
from dateutil import parser

tz = pytz.timezone('US/Eastern')
dt = datetime.now()
current_time = tz.localize(dt)
expiration_time = current_time + timedelta(seconds=3600)

logger = logging.getLogger(__name__)

# Create your views here.

# Movie Views
# Movie Details
class movieList(APIView):
    queryset = movies.objects.all()
    serializer_class = movieSerializer

    def get(self, request, format=None):
        movie = movies.objects.all()[:20]
        movie_serializer  = movieSerializer(movie, many = True)
        return Response(movie_serializer.data)

# single object using the slug
class movieObject(APIView):
    def get_movie(self, slug):
        try:
            return movies.objects.get(slug=slug)
        except movies.DoesNotExist:
            raise NotFound

    def get(self, request, slug, format=None):
        movie_object = self.get_movie(slug)
        movie_serializer = movieSerializer(movie_object)
        return Response(movie_serializer.data)

class createMovieSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createMovieSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('title')
            sanitized_title = title.replace(" ", "")
            image_file_name = request.data.get('image')
            sanitized_image = image_file_name.replace(" ", "")
            image_path      = f'content/movies/{sanitized_title}/{sanitized_image}'
            video_file_name = request.data.get('movie')
            sanitized_video = video_file_name.replace(" ", "")
            video_path      = f'content/movies/{sanitized_title}/{sanitized_video}'
            image_signed_url= make_signed_upload_url('api-dot-nwplustv-bbc5a', image_path)     
            video_signed_url = make_signed_upload_url('api-dot-nwplustv-bbc5a', video_path)
            return JsonResponse({'image_signed_url': image_signed_url, 'movie_signed_url': video_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class createMovieView(ListCreateAPIView):
    def post(self, request, format=None): 
        serializer = createMovieSerializer(data=request.data) 
        if serializer.is_valid():
            title = serializer.validated_data['title']
            existing_movie = movies.objects.filter(title=title).first()
            if existing_movie:
                Message =  ' Data already exists'
                return Response(message=Message, status=status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)  
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class createMovieMetaDataView(APIView):
    def post(self, request, format=None):
        serializer = createMovieMetadataSerializer(data=request.data)
        if serializer.is_valid():  
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        else: 
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieSearchView(APIView):
    def get(self, request, format=None):
        query = request.GET.get('query', '')
        movie = movies.objects.filter(title__icontains=query)
        serializer = movieSerializer(movie, many=True)
        return Response(serializer.data)
    

#podcasts
#Combined podcasts
class PodcastObjectList(APIView):
    def get(self, request, format=None):
        podcasts            =podcastDetails.objects.all()[:10]
        podcasts_serializer =podcastDetailsSerializer(podcasts, many=True)

        feeds               =RSSFeedDetails.objects.all()[:10]
        feeds_serializer    =RSSFeedDetailsSerializer(feeds, many=True)

        combined_data =  list(podcasts_serializer.data) + list(feeds_serializer.data)
        return Response(combined_data)
    
    def post(self, request, format=None):
        details_serializer = createPodcastDetailserializer(data=request.data['details'])
        details_serializer.is_valid(raise_exception=True)
        details = details_serializer.save()
        episodes_serializer = createPodcastEpisodeSerializer(data=request.data['episodes'], many=True)
        episodes_serializer.is_valid(raise_exception=True)
        episodes = episodes_serializer.save(podcast_detail=details)

        data = {
            'details': details_serializer.data,
            'episodes': episodes_serializer.data
        }

        return Response(data, status=status.HTTP_201_CREATED)


class PodcastObject(APIView):
    def get(self, request, slug, format=None):
        # Get all podcasts and feeds
        podcasts = podcastDetails.objects.all()
        feeds = RSSFeedDetails.objects.all()

        # Serial  ize the data
        podcasts_serializer = podcastDetailsSerializer(podcasts, many=True)
        feeds_serializer = RSSFeedDetailsSerializer(feeds, many=True)

        # Combine the data
        combined_data = list(podcasts_serializer.data) + list(feeds_serializer.data)

        # Filter the data based on the slug value
        filtered_data = [item for item in combined_data if item.get('slug') == slug]

        return Response(filtered_data)

class createPodcastDetailSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createPodcastDetailSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('title')
            sanitized_title = title.replace(" ", "")
            image_file_name = request.data.get('image') 
            sanitized_image = image_file_name.replace(" ", "")
            image_path      = f'content/podcasts/{sanitized_title}/{sanitized_image}'
            image_signed_url= make_signed_upload_url('api-dot-nwplustv-bbc5a', image_path)     
            return JsonResponse({'image_signed_url': image_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class createPodcastEpisodeSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createPodcastEpisodeSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('podcastTitle')
            sanitized_title = title.replace(" ", "")
            episode_title   = request.data.get('episodeTitle')
            audio_file_name = request.data.get('episode')
            sanitized_audio = audio_file_name.replace(" ", "")
            audio_path      = f'content/movies/{sanitized_title}/{sanitized_audio}'     
            audio_signed_url = make_signed_upload_url('api-dot-nwplustv-bbc5a', audio_path)
            return JsonResponse({'episode_signed_url': audio_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class createPodcastDetailView(APIView):    
    def post(self, request, format=None):
        serializer = createPodcastDetailserializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            existing_podcast = podcastDetails.objects.filter(title=title).first()
            if existing_podcast:
                Message =  ' Data already exists'
                return Response(message=Message, status=status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class createPodcastEpisodesView(APIView):
    def post(self, request, format=None):
        serializer = createPodcastEpisodeSerializer(data=request.data)
        if serializer.is_valid():
            podcast_title = serializer.validated_data['podcastTitle']
            podcast = podcastDetails.objects.get(title=podcast_title)
            serializer.save(podcast=podcast)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class createPodcastDetailMetaDataView(APIView):
    def post(self, request, format=None):
        serializer = createPodcastDetailMetadataSerializer(data=request.data)
        if serializer.is_valid():
            podcast_title = serializer.validated_data['podcastTitle']
            podcast = podcastDetails.objects.get(title=podcast_title)
            serializer.save(podcast=podcast)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#shows
class showDetailsList(APIView):
    def get(self, request, format=None):
        show = showDetails.objects.all()[:20]
        show_serializer = showDetailsSerializer(show, many = True)
        return Response(show_serializer.data)

# A single show object
class showObject(APIView):
    def get_show(self, slug):
        try:
            return showDetails.objects.get(slug=slug)
        except:
            raise NotFound

    def get(self, request, slug, format=None):
        show_object = self.get_show(slug)
        show_serializer = showDetailsSerializer(show_object)
        return Response(show_serializer.data)

class createShowDetailSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createShowDetailSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('title')
            sanitized_title = title.replace(" ", "")
            image_file_name = request.data.get('image') 
            sanitized_image = image_file_name.replace(" ", "")
            image_path      = f'content/shows/{sanitized_title}/{sanitized_image}'
            image_signed_url= make_signed_upload_url('api-dot-nwplustv-bbc5a', image_path)     
            return JsonResponse({'image_signed_url': image_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class createSeasonDetailSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createSeasonDetailSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('showTitle')
            sanitized_title = title.replace(" ", "")
            image_file_name = request.data.get('image') 
            sanitized_image = image_file_name.replace(" ", "")
            image_path      = f'content/shows/{sanitized_title}/{sanitized_image}'
            image_signed_url= make_signed_upload_url('api-dot-nwplustv-bbc5a', image_path)     
            return JsonResponse({'image_signed_url': image_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class createShowEpisodeSignedUrl(APIView):
    def post(self, request, format =None):
        serializer = createShowEpisodeSignedUrlSerializer(data=request.data) 
        if serializer.is_valid():
            title           = request.data.get('showTitle')
            sanitized_title = title.replace(" ", "")
            episode_title   = request.data.get('episodeTitle')
            video_file_name = request.data.get('episode')
            sanitized_video = video_file_name.replace(" ", "")
            video_path      = f'content/shows/{sanitized_title}/{sanitized_video}'     
            video_signed_url = make_signed_upload_url('api-dot-nwplustv-bbc5a', video_path)
            return JsonResponse({'episode_signed_url': video_signed_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class createShowDetailView(APIView):    
    def post(self, request, format=None):
        serializer = createShowDetailserializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            existing_show = showDetails.objects.filter(title=title).first()
            if existing_show:
                Message =  ' Data already exists'
                return Response(message=Message, status=status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class createseasonDetailView(APIView):    
    def post(self, request, format=None):
        serializer = createSeasonDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class createshowEpisodeView(APIView):
    def post(self, request, format=None):
        serializer = createShowEpisodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class createShowDetailMetaDataView(APIView):
    def post(self, request, format=None):
        serializer = createShowDetailMetadataSerializer(data=request.data)
        if serializer.is_valid():  
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class createRSSFeedUrlView(APIView):
    def post(self, request, format=None):
        serializer = createRSSDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class updateFeeds(APIView):
    def get(self, request):
        feed_urls = RSSFeedDetails.objects.values_list('url', flat=True)
        for url in feed_urls:
            feed = feedparser.parse(url)
            if not feed:
                # Handle invalid feed URL
                continue
            
            rss_feed_detail = RSSFeedDetails.objects.get(url=url)

            # Check if the RSS feed already exists in the database
            rss_feed_item = RSSFeedItems.objects.filter(rssFeedDetail=rss_feed_detail).order_by('-date_published').first()
            last_published = rss_feed_item.date_published if rss_feed_item else None

            # Process new entries
            new_entries = []
            for entry in feed.entries:
                published = parser.parse(entry.published).strftime('%Y-%m-%d %H:%M:%S%z')
                published_datetime = datetime.strptime(published, '%Y-%m-%d %H:%M:%S%z')
                if last_published and last_published >= published_datetime:
                    # No new RSS feed items
                    break

                # Create a new RSS feed item
                new_entry = RSSFeedItems(
                    rssFeedDetail=rss_feed_detail,
                    episodeTitle=entry.title,
                    episodeDesc=entry.description,
                    episode=entry.enclosures[0].url,
                    date_published=published
                )
                new_entries.append(new_entry)
                if new_entries:
                    RSSFeedItems.objects.bulk_create(new_entries)
                
                # Update the episode metadata
                duration = entry.get('itunes_duration', '')
                if duration:
                    duration = duration.strip()
                    if re.match(r'\d{2}:\d{2}:\d{2}', duration):
                        # duration is already in the format of hours:minutes:seconds
                        meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed_item)
                        meta_data.duration = duration
                        meta_data.save()

                    elif re.match(r'\d{1,2}:\d{2}', duration):
                        # duration is in the format of minutes:seconds
                        duration_parts = duration.split(':')
                        duration_secs = int(duration_parts[0]) * 60 + int(duration_parts[1])
                        duration = timedelta(seconds=duration_secs)
                        duration_str = (datetime.min + duration).time().strftime('%H:%M:%S')
                        meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed_item)
                        meta_data.duration = duration_str
                        meta_data.save()
                    else:
                        # duration is in seconds and needs to be converted
                        duration = timedelta(seconds=int(duration))
                        duration_str = (datetime.min + duration).time().strftime('%H:%M:%S')
                        meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed_item)
                        meta_data.duration = duration_str
                        meta_data.save()

        return Response('RSS feed update successful.')




#ContentFiltering
class ContentThemeView(ListAPIView):
    serializer_class = contentDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['contentTheme']

    def get_queryset(self):
        theme = self.kwargs.get('contentTheme')
        print('theme:', theme)
        movies_query = movies.objects.filter(contentTheme=theme)[:20]
        podcasts = podcastDetails.objects.filter(contentTheme=theme)[:20]
        shows = showDetails.objects.filter(contentTheme=theme)[:20]
        feeds = RSSFeedDetails.objects.filter(contentTheme=theme)[:20]

        results = list(movies_query) + list(podcasts) + list(shows) + list(feeds)
        return results

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = contentDetailSerializer(queryset)
        return Response(serializer.data)


class SearchView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        movie = movies.objects.filter(Q(title__icontains=query) | Q(contentTheme__icontains=query))
        shows = showDetails.objects.filter(Q(title__icontains=query) | Q(contentTheme__icontains=query))
        
        podcasts = podcastDetails.objects.filter(Q(title__icontains=query) | Q(contentTheme__icontains=query))
        feeds = RSSFeedDetails.objects.filter(Q(title__icontains=query) | Q(contentTheme__icontains=query))

        movie_serializer = movieSerializer(movie, many=True)
        show_serializer = showDetailsSerializer(shows, many=True)
        podcasts_serializer = podcastDetailsSerializer(podcasts, many=True)
        feeds_serializer = RSSFeedDetailsSerializer(feeds, many=True)

        # Combine the data
        combined_data = list(podcasts_serializer.data) + list(feeds_serializer.data)
        return Response({
            'movies': movie_serializer.data,
            'shows': show_serializer.data,
            'podcasts': combined_data,
        })

# Form view to test signed urls


def create_movie_view(request):
    context = {}
    form = CreateMovieForm()
    if request.method == 'POST':

        # if form.is_valid():
        obj = form.save(commit=False)
        image_file = request.POST.get('image')
        video_file = request.POST.get('movie')
        image_signed_url = make_signed_upload_url(
            'api-dot-nwplustv-bbc5a', image_file)
        video_signed_url = make_signed_upload_url(
            'api-dot-nwplustv-bbc5a', video_file)
        print(image_signed_url, video_signed_url)
        context['image_signed_url'] = image_signed_url
        context['video_signed_url'] = video_signed_url
        context['csrf_token'] = get_token(request)

        return JsonResponse(context)
        # else:
        # context['form'] = form
        # return render(request, 'movie.html', context)

    else:
        form = CreateMovieForm()
        context['form'] = form
        return render(request, 'movie.html', context)
    return render(request, 'movie.html', context)


def make_signed_upload_url(
    bucket: str,
    blob: str,
    *,
    exp: Optional[timedelta] = None,
    content_type="application/octet-stream",
    min_size=1,
    max_size=int(1e12),
):

    if exp is None:
        exp = timedelta(hours=1)

    client = settings.STORAGE_CLIENT
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(blob)
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=exp,
        service_account_email=settings.STORAGE_CLIENT.project,
        method="PUT",

    )

    return signed_url
