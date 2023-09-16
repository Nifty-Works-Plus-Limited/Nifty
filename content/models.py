from django.db import models
from django.conf import settings
import sys
import feedparser
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
#sys.path.append('./functions/upload_location.py')
from .functions.upload_location import uploadLocation
from datetime import datetime

location = uploadLocation

FAMILY = 'Family'
LIFESTYLE = 'Lifestyle'
KIDS = 'Kids'
ANIMATIONS = 'Animation'

contentTheme=(
    (FAMILY,'FAMILY'),
    (LIFESTYLE,'LIFESTYLE'),
    (KIDS,'KIDS'),
    (ANIMATIONS,'ANIMATIONS')
    )
# Create your models here.
class movies(models.Model):
    title               =models.CharField(max_length=50, null=False, blank=False )
    desc                =models.TextField(max_length=5000, null=False, blank=False, verbose_name="Content Description")
    image               =models.CharField(max_length=500, null=False, blank=False, verbose_name="thumbnail")
    movie               =models.CharField(max_length=500, null=False, blank=True)     
    contentTheme        =models.CharField(max_length=50, choices =contentTheme, default=FAMILY, null=False, blank=False)
    slug 			    =models.SlugField(blank=True, unique=True)
    converted_path      =models.CharField(max_length=500, null=True)
    is_converted        =models.BooleanField(default=False)
    date_published 		=models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 		=models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Movie"

    def __str__(self):
        return str(self.title)

class movieMetaData(models.Model):
    movieDetail       =models.OneToOneField(movies, on_delete=models.CASCADE, related_name="movie_metadata", related_query_name="movie_metadata")
    duration    =models.TimeField(null=True, blank=True)
    director    =models.CharField(max_length=500, null=False, blank=True)
    year        =models.IntegerField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.movie.title}"

class podcastDetails(models.Model):
    title               =models.CharField(max_length=500,null=False, blank=False )
    desc                =models.TextField(max_length=5000,null=False, blank=False, verbose_name="Podcast Description")
    image               =models.CharField(max_length=500,null=False, blank=True, verbose_name="thumbnail")
    contentTheme        =models.CharField(max_length=500,choices =contentTheme, default=LIFESTYLE, null=False, blank=False)
    slug 				=models.SlugField(max_length=500,blank=True, unique=True)
    date_published 		=models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 		=models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Podcast Detail"

    def __str__(self):
        return self.title
class podcastEpisodes(models.Model):
    podcastDetail      =models.ForeignKey(podcastDetails, max_length=50, null=False, blank=False, on_delete=models.CASCADE, related_name="podcastepisodes", related_query_name="podcastepisode" )
    episodeTitle        =models.CharField(max_length=500, null=False, blank=True)
    episodeDesc         =models.TextField(max_length=5000, null=False, blank=False, verbose_name="Episode Description")
    episode             =models.CharField(max_length=500, null=False, blank=True, verbose_name="Podcast Episode")
    slug                =models.SlugField(blank=True, unique=True)
    converted_path      =models.CharField(max_length=500, null=True)
    is_converted        =models.BooleanField(default=False)
    date_published 		=models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 		=models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Podcast Episodes"

    def __str__(self):
        return str(self.title) + "-" + str(self.episodeTitle)
    
class podcastDetailMetaData(models.Model):
    podcastDetail   =models.OneToOneField(podcastDetails, on_delete=models.CASCADE, related_name='podcast_detail_metadata')
    author          =models.CharField(max_length=500, null=False, blank=True)

class podcastEpisodeMetaData(models.Model):
    podcastEpisode = models.OneToOneField(podcastEpisodes, on_delete=models.CASCADE, related_name="podcast_episode_metadata")
    duration = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.episode.title} - {self.episode.episodeTitle}"

class showDetails(models.Model):
    title               =models.CharField(max_length=50, null=False, blank=False )
    desc                =models.TextField(max_length=5000, null=False, blank=False, verbose_name="show Description")
    image               =models.CharField(max_length=500, null=False, blank=True, verbose_name="thumbnail")
    contentTheme        =models.CharField(max_length=50, choices =contentTheme, default=FAMILY, null=False, blank=False)
    slug 				=models.SlugField(max_length=500, blank=True, unique=True)
    date_published 		=models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 		=models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Show Detail"

    def __str__(self):
        return self.title
class seasonDetails(models.Model):
    showDetail      =models.ForeignKey(showDetails, on_delete=models.CASCADE, related_name="seasons", related_query_name="season")
    no              =models.IntegerField(help_text="season number", blank=False, null=False)
    desc            =models.TextField(max_length=5000, null=False, blank=True, verbose_name="Show Description")
    image           =models.CharField(max_length=500, null=False, blank=True, verbose_name="thumbnail")
    slug 			=models.SlugField(blank=True, unique=True)
    date_published  =models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 	=models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Season Detail"

    def __str__(self):
        return str(self.title) + "-" + str(self.no)
class seasonEpisodes(models.Model):
    showDetail          =models.ForeignKey(showDetails, on_delete=models.CASCADE)
    seasonDetail        =models.ForeignKey(seasonDetails, default='1', on_delete=models.CASCADE, related_name="seasonEpisodes", related_query_name="seasonEpisode")
    episodeTitle        =models.CharField(max_length=50, blank=True, null=False)
    episodeDesc         =models.TextField(max_length=5000, blank=True, null=False)
    episode             =models.CharField(max_length=500, null=False, blank=True)    
    slug 			    =models.SlugField(blank=True, unique=True)
    converted_path      =models.CharField(max_length=500, null=True)
    is_converted        =models.BooleanField(default=False)
    date_published      =models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 	    =models.DateTimeField(auto_now=True, verbose_name="date updated")

    class Meta:
        verbose_name = "Series Episode"

    def __str__(self):
        return self.episodeTitle
    
class showMetaData(models.Model):
    showDetail      =models.OneToOneField(showDetails, on_delete=models.CASCADE, related_name='show_detail_metadata')
    director        =models.CharField(max_length=500, null=False, blank=True)
    year            =models.IntegerField(max_length=500, null=True, blank=True)


class showEpisodesMetaData(models.Model):
    seasonEpisode = models.ForeignKey(seasonEpisodes, on_delete=models.CASCADE, related_name="show_metadata")
    duration = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.showEpisode.showTitle} - {self.showEpisode.showSeason} - {self.showEpisode.episodeTitle}"
class RSSFeedDetails(models.Model):
    url             =models.URLField(unique=True)
    contentTheme    =models.CharField(max_length=50, choices =contentTheme, default=LIFESTYLE, null=False, blank=False)
    title           =models.CharField(max_length=300, null=True, blank=True)
    description     =models.TextField(null=True, blank=True)
    image           =models.URLField(null=True, blank=True)
    slug            =models.SlugField(blank=True, unique=True)
    date_published  =models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated 	=models.DateTimeField(auto_now=True, verbose_name="date updated")
    

    #def __str__(self):
    #    return self.title




class RSSFeedItems(models.Model):
    rssFeedDetail       =models.ForeignKey(RSSFeedDetails, on_delete=models.CASCADE, related_name ='feeds', related_query_name='feed')
    episodeTitle        =models.CharField(max_length=300)
    episodeDesc         =models.TextField(max_length=5000)
    episode             =models.URLField()
    date_published      =models.DateTimeField(null=True, blank=True)
    date_updated        =models.DateTimeField(auto_now=True, verbose_name="date updated")


    def _str_(self):
        return self.title
    
class RSSMetaData(models.Model):
    rssDetail       =models.OneToOneField(RSSFeedDetails, on_delete=models.CASCADE, related_name='rss_detail_metadata')
    author          =models.CharField(max_length=500, null=False, blank=True)

class RSSEpisodesMetaData(models.Model):
    rssEpisode  = models.ForeignKey(RSSFeedItems, on_delete=models.CASCADE, related_name="rss_episode_metadata")
    duration    = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.podcastEpisode.title} - {self.podcastEpisode.episodeTitle}"






