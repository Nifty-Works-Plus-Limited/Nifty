import base64
import json
import os
import re
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from io import BytesIO
from content.models import *
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from dateutil import parser
import ssl
from moviepy.editor import AudioFileClip
from datetime import timedelta, datetime
ssl._create_default_https_context=ssl._create_unverified_context
from google.cloud import pubsub_v1, storage
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
import urllib.request
import json
from google.auth import compute_engine
from google.oauth2 import id_token
import requests
from io import BytesIO

def video_converter(sender, id, file_path):
    
	if not file_path:
		return 'Error: file_name is empty'
	start_index = file_path.find("content/")
	if start_index == -1:
		start_index = 0
	else:
		start_index += len("content/")
	file_path = f"content/{file_path[start_index:]}"

	payload = {
        'sender': sender.__name__,
        'id': id,
        'file_path': file_path
    }

	audience = 'https://convert-video-32o5e43wyq-uc.a.run.app'

	auth_req = google.auth.transport.requests.Request()
	id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
	print(id_token)

	# Construct the request headers
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {id_token}'
	}

	# Make the request
	endpoint = 'https://convert-video-32o5e43wyq-uc.a.run.app'
	response = requests.post(endpoint, json.dumps(payload).encode(), headers=headers)

	if response.ok:
		return f'Successfully triggered function: {response.text}'
	else:
		return f'Error: {response.status_code} - {response.reason}'
	
	

def get_rss_duration(file_path):
	response	=requests.get(f'{file_path}')
	audio_file	=BytesIO(response.content)

	directory = 'C:\\temp'
	if not os.path.exists(directory):
		os.mkdir(directory)

	# Download the file to a temporary location
	temp_file = os.path.join(directory, 'temp_file.mp3')
	with open(temp_file, 'wb') as f:
		f.write(audio_file.getbuffer())

	audio = AudioFileClip(temp_file)

	duration = timedelta(seconds=audio.duration)
	duration = (datetime.min + duration).time().strftime('%H:%M:%S')

	audio.close()
	return duration

#Movie Signals

@receiver(pre_save, sender=movies)
def pre_save_movies_post_receiever(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(str(instance.title))

@receiver(post_save, sender=movies)
def movie_convertion(sender, instance, created, **kwargs):
	if created and not instance.is_converted:
		video_converter(sender,instance.id,instance.movie)

#PodcastDetails Signals
def pre_save_podcastDetails_post_receiver(sender,instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(str(instance.title))

pre_save.connect(pre_save_podcastDetails_post_receiver, sender=podcastDetails)

#podcastEpisode Signals
def pre_save_podcastEpisodes_post_receiver(sender,instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(str(instance.podcastDetail.title) + "-" + str(instance.episodeTitle))

pre_save.connect(pre_save_podcastEpisodes_post_receiver, sender=podcastEpisodes)

#@receiver(post_save, sender=podcastEpisodes)
#def podcastEpisode_convertion(sender, instance, **kwargs):
#	if instance.is_converted:
#		print('convertion has already happened')
#	else:
#		video_converter(sender,instance.id,instance.episode)

#showDetails Signals
def pre_save_contentDetails_post_receiever(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(str(instance.title))

pre_save.connect(pre_save_contentDetails_post_receiever, sender=showDetails)

#SeasonDetails Signals
def pre_save_seasonDetails_post_receiever(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(str(instance.showDetail.title) + "-" + str(instance.no))

pre_save.connect(pre_save_seasonDetails_post_receiever, sender=seasonDetails)

#Show Signals
def pre_save_content_post_receiever(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = slugify(str (instance.showDetail.title)+"-" + (str(instance.seasonDetail.no)) + "-" + str(instance.episodeTitle))
pre_save.connect(pre_save_content_post_receiever, sender=seasonEpisodes)

@receiver(post_save, sender=seasonEpisodes)
def seasonEpisode_convertion(sender, instance, **kwargs):
	if instance.is_converted:
		print('convertion has already happened')
	else:
		video_converter(sender,instance.id,instance.episode)

#getting RSSFeed Details
@receiver(pre_save, sender=RSSFeedDetails)
def rss_details(sender, instance, **kwargs):
	feed = feedparser.parse(instance.url)
	if not feed:
		# handle invalid feed url
		return print('invalid feed')
	instance.title = feed.feed.title
	instance.description = feed.feed.description
	if 'image' in feed.feed:
		instance.image = feed.feed.image.href

# getting RSS Feed Episode details
@receiver(post_save, sender=RSSFeedDetails)
def updateRSSFeedItems(sender, instance, created, **kwargs):
	if not instance.slug:
		instance.slug	=slugify(str(instance.title) + "-" + str(instance.id))
		instance.save()

	if created:
		url = instance.url
		feed    = feedparser.parse(url)
		entries = reversed(feed.entries)
		#feed_url, created = RSSFeedURL.objects.get_or_create(url = url)
		for entry in entries:
			published	=parser.parse(entry.published).strftime(('%Y-%m-%d %H:%M:%S%z'))
			feed_url, created	=RSSFeedDetails.objects.get_or_create(url = url)
			rss_feed = RSSFeedItems.objects.create(
				rssFeedDetail 		=instance,
				episodeTitle		=entry.title,
				episodeDesc			=entry.description,
				episode 			=entry.enclosures[0].url,
				date_published		=published

			)
			duration = entry['itunes_duration']
			if re.match(r'\d{2}:\d{2}:\d{2}', duration):
				# duration is already in the format of hours:minutes:seconds
				meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed)
				meta_data.duration = duration
				meta_data.save()

			elif re.match(r'\d{1,2}:\d{2}', duration):
				# duration is in the format of minutes:seconds
				duration_parts = duration.split(':')
				duration_secs = int(duration_parts[0]) * 60 + int(duration_parts[1])
				duration = timedelta(seconds=duration_secs)
				duration_str = (datetime.min + duration).time().strftime('%H:%M:%S')
				meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed)
				meta_data.duration = duration_str
				meta_data.save()
			else:
				# duration is in seconds and needs to be converted
				duration = timedelta(seconds=int(duration))
				duration_str = (datetime.min + duration).time().strftime('%H:%M:%S')
				meta_data, created = RSSEpisodesMetaData.objects.get_or_create(rssEpisode=rss_feed)
				meta_data.duration = duration_str
				meta_data.save()
				
			





