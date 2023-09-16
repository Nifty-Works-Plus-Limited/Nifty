from django.contrib import admin
from content.models import *
# Register your models here.

admin.site.register(movies)
admin.site.register(podcastDetails)
admin.site.register(podcastEpisodes)
admin.site.register(showDetails)
admin.site.register(seasonDetails)
admin.site.register(seasonEpisodes)
admin.site.register(RSSFeedDetails)