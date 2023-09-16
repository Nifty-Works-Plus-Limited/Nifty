from moviepy.editor import VideoFileClip
from content.models import *
class uploadLocation():

    #upload a movie
    def movie_location(instance, filename, **kwargs):
        file_path = 'content/movies/{title}/{filename}'.format(
            title= str(instance.title), filename= filename
        )

        return  file_path 
                
    #podcast Details
    def podcast_location(instance, filename, **kwargs):
        file_path = 'content/podcasts/{title}/{filename}'.format(
                title=str(instance.title), filename=filename
            ) 
        return file_path
    
    #Podcast Episode Files
    def podcastEpisodes_location(instance, filename, **kwargs):
        file_path = 'content/podcasts/{title}/{episodeTitle}/{filename}'.format(
            title = str(instance.title), episodeTitle = str(instance.episodeTitle), filename = filename
        )
        return file_path

    def show_location(instance, filename, **kwargs):
        file_path = 'content/shows/{title}/{filename}'.format(
                title = str(instance.title),  filename=filename
            ) 
        return file_path

    def season_location(instance, filename, **kwargs):
        file_path = 'content/shows/{title}/{no}/{filename}'.format(
                title = str(instance.title), no=str(instance.no), filename=filename
            ) 
        return file_path

    def seasonEpisodes_location(instance, filename, **kwargs):
        file_path = 'content/shows/{title}/{no}/episodes/{filename}'.format(
            title= str(instance.showTitle), no=str(instance.showSeason), filename= filename
        )
        return file_path

   

