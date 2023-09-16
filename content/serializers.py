from rest_framework import serializers
from content.models import *
bucket = settings.UPLOAD_BUCKET 
upload_bucket = f'https://storage.googleapis.com/{bucket}'

#Movie Serializers
class movieMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = movieMetaData
        fields = ['movieDetail', 'director', 'year']
class movieSerializer(serializers.ModelSerializer): 
    movie_metadata = movieMetaDataSerializer()
    class Meta:
        model   =movies
        fields = ['pk', 'title', 'desc', 'image', 'movie', 'contentTheme', 'slug', 'converted_path', 'movie_metadata', 'date_published', 'date_updated']
        read_only_fields = ['pk', 'slug', 'date_published', 'date_updated']

class createMovieSignedUrlSerializer(serializers.Serializer):
    class Meta:
        model = movies
        fields = [ 'title', 'image', 'movie']

class createMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = movies
        fields = ['title', 'desc', 'image', 'movie', 'contentTheme'] 

    def create(self, validated_data):
        
        image_file_name = validated_data['image'] 
        video_file_name = validated_data['movie']
        title           = validated_data['title']
        sanitized_title = title.replace(" ", "")
        sanitized_image = image_file_name.replace(" ", "")
        sanitized_video = video_file_name.replace(" ", "")
        image_path = f"{upload_bucket}/content/movies/{sanitized_title}/{sanitized_image}"
        movie_path = f"{upload_bucket}/content/movies/{sanitized_title}/{sanitized_video}"
        instance = movies.objects.create(
            title=validated_data['title'],
            desc=validated_data['desc'],
            image=image_path,
            movie=movie_path,
            contentTheme = validated_data['contentTheme']
        )

        instance.save()
        return instance

class createMovieMetadataSerializer(serializers.ModelSerializer):
    movieTitle = serializers.CharField(max_length=500, write_only=True)
    class Meta:
        model = movieMetaData
        fields = ['movieTitle','director', 'year']
    def create(self,validated_data):
        movie_title = validated_data['movieTitle']
        try: 
            movie_detail = movies.objects.get(title = movie_title )
        except movies.DoesNotExist:
            raise serializers.ValidationError("The movie object with title {movie_title} does not exist")
        instance = movieMetaData.objects.create(
            movieDetail = movie_detail,
            director = validated_data['director'],
            year    = validated_data['year'],
        )
        instance.save()
        return instance

#Podcast Serializersclass 
class podcastEpisodesSerializer(serializers.ModelSerializer):
    class Meta:
        model   = podcastEpisodes
        fields  = ['pk', 'podcastDetail', 'episodeTitle', 'episodeDesc', 'episode', 'slug']

class podcastDetailMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = podcastDetailMetaData
        fields = ['podcastDetail', 'author']
class podcastDetailsSerializer(serializers.ModelSerializer):
    podcastepisodes = podcastEpisodesSerializer(many = True), 
    podcast_detail_metadata = podcastDetailMetaDataSerializer()
    class Meta:
        model   =podcastDetails
        fields  =['pk', 'title', 'desc', 'image', 'contentTheme', 'slug', 'podcastepisodes', 'podcast_detail_metadata']

    
#create serializers
class createPodcastDetailSignedUrlSerializer(serializers.Serializer):
    class Meta:
        fields = [ 'title', 'image']
class createPodcastDetailserializer(serializers.ModelSerializer):
    class Meta:
        model = podcastDetails
        fields = ['pk', 'title', 'desc', 'image', 'contentTheme', 'slug', 'date_published', 'date_updated']
        read_only_fields = ['pk', 'slug', 'date_published', 'date_updated']

    def create(self, validated_data):
        image_file_name = validated_data['image']
        title           = validated_data['title']
        sanitized_title = title.replace(" ", "")
        sanitized_image = image_file_name.replace(" ", "")
        image_path = f"{upload_bucket}/content/podcasts/{sanitized_title}/{sanitized_image}"
        instance = podcastDetails.objects.create(
            title=validated_data['title'],
            desc=validated_data['desc'],
            image=image_path,
            contentTheme = validated_data['contentTheme']
        )

        instance.save()
        return instance

class createPodcastEpisodeSignedUrlSerializer(serializers.Serializer):
    #podcastTitle = serializers.CharField(max_length=500, write_only=True)
    class Meta:
        fields = ['podcastTitle', 'title', 'episode']
class createPodcastEpisodeSerializer(serializers.ModelSerializer):
    podcastTitle = serializers.CharField(write_only=True, max_length=500)
    # Other fields

    class Meta:
        model = podcastEpisodes
        fields = ['pk', 'podcastTitle', 'episodeTitle', 'episodeDesc', 'episode', 'slug', 'date_published', 'date_updated']
        read_only_fields = ('pk', 'slug', 'date_published', 'date_updated')
    
    def create(self, validated_data):
        podcast_title = validated_data['podcastTitle']
        
        try:
            podcast_details = podcastDetails.objects.get(title=podcast_title)
        except podcastDetails.DoesNotExist:
            raise serializers.ValidationError(f"Podcast details object with title '{podcast_title}' does not exist")
        sanitized_title = podcast_title.replace(" ", "")
        episode_title = validated_data['episodeTitle']
        audio_file_name = validated_data['episode']
        sanitized_audio = audio_file_name.replace(" ", "")
        audio_path = f'{upload_bucket}/content/podcasts/{sanitized_title}/{sanitized_audio}'

        instance = podcastEpisodes.objects.create(
            podcastDetail=podcast_details,
            episodeTitle=episode_title,
            episodeDesc=validated_data.get('episodeDesc', ''),
            episode=audio_path,
        )
        instance.save()
        return instance

class createPodcastDetailMetadataSerializer(serializers.ModelSerializer):
    podcastTitle = serializers.CharField(max_length=500, write_only=True)
    class Meta:
        model = podcastDetailMetaData
        fields = ['podcastTitle','author']
    def create(self, validated_data):
        podcast_title = validated_data['podcastTitle']
        try:
            podcast_detail = podcastDetails.objects.get(title= podcast_title)
        except podcastDetails.DoesNotExist:
            raise serializers.ValidationError("Podcast Title {podcast_title} does not exist")
        instance = podcastDetailMetaData.objects.create(
            podcastDetail = podcast_detail,
            author = validated_data['author'],
            )
        instance.save()
        return instance


#show serializers        
class seasonEpisodesSerializer(serializers.ModelSerializer):
    class Meta:
        model   =seasonEpisodes
        fields  =['pk','seasonDetail','episodeTitle','episodeDesc','episode', 'converted_path', 'slug']


class seasonDetailsSerializer(serializers.ModelSerializer): 
    seasonEpisodes   =seasonEpisodesSerializer(many=True)
    class Meta:
        model   =seasonDetails
        fields  =['pk','showDetail', 'no', 'desc', 'image', 'slug', 'seasonEpisodes']


class showDetailMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = showMetaData
        fields = ['showDetail', 'director', 'year']

class showDetailsSerializer(serializers.ModelSerializer):
    seasons = seasonDetailsSerializer(many=True, read_only=True)
    show_detail_metadata = showDetailMetaDataSerializer()
    class Meta:
        model   =showDetails
        fields  =['pk','title', 'desc', 'image', 'contentTheme', 'slug', 'seasons', 'show_detail_metadata']

class createShowDetailSignedUrlSerializer(serializers.Serializer):
    class Meta:
        fields = [ 'title', 'image']

class createShowDetailserializer(serializers.ModelSerializer):
    class Meta:
        model = showDetails
        fields = ['pk', 'title', 'desc', 'image', 'contentTheme', 'slug', 'date_published', 'date_updated']
        read_only_fields = ['pk', 'slug', 'date_published', 'date_updated']

    def create(self, validated_data):
        image_file_name = validated_data['image']
        title           = validated_data['title']
        sanitized_title = title.replace(" ", "")
        sanitized_image = image_file_name.replace(" ", "")
        image_path      =f'{upload_bucket}/content/shows/{sanitized_title}/{sanitized_image}'
        instance = showDetails.objects.create(
            title           =title,
            desc            =validated_data['desc'],
            image           =image_path,
            contentTheme    =validated_data['contentTheme']
        )
        instance.save()
        return instance

class createSeasonDetailSignedUrlSerializer(serializers.Serializer):
    class Meta:
        fields = [ 'showDetail', 'no', 'image']

class createSeasonDetailSerializer(serializers.ModelSerializer):
    showTitle     = serializers.CharField(write_only=True, max_length=500)
    #image = serializers.CharField(max_length=500)

    class Meta:
        model = seasonDetails
        fields = ['pk', 'showTitle', 'no', 'desc', 'image','slug', 'date_published', 'date_updated']
        read_only_fields = ['pk', 'slug', 'date_published', 'date_updated']
    
    def create(self, validated_data):
        show_title  =validated_data['showTitle']
        try:
            show_detail = showDetails.objects.get(title=show_title)
        except:
            raise serializers.ValidationError(f"show details object with title '{show_title}' does not exist")
        sanitized_title = show_title.replace(" ", "")
        no              =validated_data['no']
        image_file_name = validated_data['image']
        sanitized_image = image_file_name.replace(" ", "")
        image_path      =f'{upload_bucket}/content/shows/{sanitized_title}/{sanitized_image}'
        instance = seasonDetails.objects.create(
            showDetail  =show_detail,
            no          =no,
            desc        =validated_data['desc'],
            image       =image_path

        )

        instance.save()
        return instance

class createShowEpisodeSignedUrlSerializer(serializers.Serializer):
    #showTitle = serializers.CharField(max_length = 500, write_only=True)
    #seasonNo = serializers.IntegerField(write_only=True)
    class Meta:
        fields = [ 'showTitle', 'seasonNo', 'episode']

class createShowEpisodeSerializer(serializers.ModelSerializer):
    showTitle       =serializers.CharField(write_only=True, max_length=500)
    seasonNo        =serializers.IntegerField(write_only=True)

    class Meta:
        model = seasonEpisodes
        fields = ('pk', 'showTitle', 'seasonNo', 'episodeTitle', 'episodeDesc', 'episode', 'slug', 'date_published', 'date_updated')
        read_only_fields = ('pk', 'slug', 'date_published', 'date_updated')
    
    def create(self, validated_data):
        show_title      =validated_data['showTitle']
        season_no       =validated_data['seasonNo']
        try:
            show_detail = showDetails.objects.get(title=show_title)
            season_detail = seasonDetails.objects.filter(no=season_no, showDetail=show_detail)
            if not season_detail.exists():
                raise seasonDetails.DoesNotExist()
            season_detail = season_detail.first()
        except showDetails.DoesNotExist:
            raise serializers.ValidationError(f"The show Detail with title {show_title} does not exist")
        except seasonDetails.DoesNotExist:
            raise serializers.ValidationError(f"The season no {season_no} does not exist for the show Detail with title {show_title}")

        sanitized_title = show_title.replace(" ", "")
        video_file_name =validated_data['episode']
        sanitized_video = video_file_name.replace(" ", "")
        episode_title   =validated_data['episodeTitle']
        video_path  =f'{upload_bucket}/content/shows/{sanitized_title}/{sanitized_video}'

        instance = seasonEpisodes.objects.create(
            showDetail      =show_detail,
            seasonDetail    =season_detail,
            episodeTitle    =episode_title,
            episodeDesc     =validated_data['episodeDesc'],
            episode         =video_path
        )

        instance.save()
        return instance
class createShowDetailMetadataSerializer(serializers.ModelSerializer):
    showTitle = serializers.CharField(write_only=True, max_length = 500)
    class Meta:
        model = showMetaData
        fields = ['showTitle', 'director', 'year']
    def create(self, validated_data):
        show_title = validated_data['showTitle']
        try:
            show_detail = showDetails.objects.get(title = show_title)
        except showDetails.DoesNotExist:
            raise serializers.ValidationError("The show Details of title {show_title} does not exist")
        instance = showMetaData.objects.create(
            showDetail = show_detail,
            director = validated_data['director'],
            year = validated_data['year']
        )
        instance.save()
        return  instance

class RSSFeedItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSSFeedItems
        fields = ['rssFeedDetail', 'episodeTitle', 'episodeDesc', 'episode', 'date_published']

class RSSFeedDetailsSerializer(serializers.ModelSerializer):
    feeds =RSSFeedItemsSerializer(many=True)
    class Meta:
        model = RSSFeedDetails
        fields = ['url', 'title', 'description', 'image', 'slug', 'feeds']


class createRSSDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model   =RSSFeedDetails
        fields  = ['url']

    def creater(self, validated_data):
        instance = RSSFeedDetails.objects.create(
            url = validated_data['url']
        )
        instance.save()
        return instance

class CombinedSerializer(serializers.Serializer):
    podcast_details = podcastDetailsSerializer()
    rss_feed_details = RSSFeedDetailsSerializer()

    def to_representation(self, instance):
        podcast_data = podcastDetailsSerializer(instance.podcast).data
        rss_feed_data = RSSFeedDetailsSerializer(instance.rss_feed).data
        return {'podcast_details': podcast_data, 'rss_feed_details': rss_feed_data}

class NestedSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        return super().to_representation(data)

class contentDetailSerializer(serializers.Serializer):
    movies = movieSerializer(many=True)
    podcasts = podcastDetailsSerializer(many=True)
    shows = showDetailsSerializer(many=True)
    feeds = RSSFeedDetailsSerializer(many = True)

    class Meta:
        list_serializer_class = NestedSerializer

    def to_representation(self, instance):
        data = {
            'movies': [],
            'podcasts': [],
            'shows': [],
        }
        for obj in instance:
            if isinstance(obj, movies):
                data['movies'].append(movieSerializer(obj).data)
            elif isinstance(obj, podcastDetails):
                data['podcasts'].append(podcastDetailsSerializer(obj).data)
            elif isinstance(obj, showDetails):
                data['shows'].append(showDetailsSerializer(obj).data)
            elif isinstance(obj,RSSFeedDetails):
                data['podcasts'].append(RSSFeedDetailsSerializer(obj).data)
        return data

