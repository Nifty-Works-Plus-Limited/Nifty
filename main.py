from NiftyVODBackend.wsgi import application
import os
import tempfile
import subprocess
import uuid
from django.conf import settings
import os
import threading
from multiprocessing import Process
from moviepy.editor import concatenate_videoclips, VideoFileClip


from content.models import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

def getDBHost():
    return os.getenv('DJANGO_DATABASE_HOST')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': os.getenv('DJANGO_DATABASE_PASSWORD'),
        'HOST': getDBHost(),
        'PORT': os.getenv('DJANGO_DATABASE_PORT'),
        'OPTIONS': {'charset': 'utf8mb4'},
    },


}


# App Engine by default looks for a main.py file at the root of the app
# directory with a WSGI-compatible object called app.
# This file imports the WSGI-compatible object of your Django app,
# application from mysite/wsgi.py and renames it app so it is discoverable by
# App Engine without additional configuration.
# Alternatively, you can add a custom entrypoint field in your app.yaml:
# entrypoint: gunicorn -b :$PORT mysite.wsgi
app = application

client = settings.STORAGE_CLIENT
GS_BUCKET_NAME = settings.UPLOAD_BUCKET
GS_UPLOADHLS_BUCKET = 'hls-video-format'


def convert_video(request):
    
    bucket = client.bucket(GS_BUCKET_NAME)  
    output_id = str(uuid.uuid4())
    data = request.get_json()
    sender = data.get('sender')
    object_id = data.get('id')
    file_path = data.get('file_path')
    #dir_path, file_name = os.path.split(file_path)
    blob = bucket.blob(file_path)
    with tempfile.TemporaryDirectory(dir = '/tmp') as directory:
        output_dir = f"{directory}/output"
        temp_file = os.path.join(directory, 'temp_file.mp4')
        blob.download_to_filename(temp_file)
        duration = get_duration(temp_file)
        convert_to_resolutions(temp_file,output_id, output_dir, sender,object_id, duration)
        #save_object_instance(sender,object_id, output_id, duration)

def format_duration(duration):
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_duration(temp_file):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1', temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
    duration_str = result.stdout.decode('utf-8').strip()
    duration = float(duration_str)
    return duration

def convert_to_resolutions(temp_file,output_id, output_dir, sender,object_id, duration):
    resolutions = {
                '360p': {'w': 640, 'h': 360, 'b:v': '600k', 'b:a': '128k'},
                '480p': {'w': 854, 'h': 480, 'b:v': '1000k', 'b:a': '128k'},
                '720p': {'w': 1280, 'h': 720, 'b:v': '1500k', 'b:a': '192k'},
                '1080p': {'w': 1920, 'h': 1080, 'b:v': '2500k', 'b:a': '192k'},
    }

    # resolutions to convert to
    processes = []
    for resolution in resolutions:
        process = Process(target=convert_resolution, args=(resolution, temp_file, output_dir, output_id, resolutions, duration))
        processes.append(process)
        process.start()
    # Wait for all processes to finish
    for process in processes:
            process.join()
    # Create master playlist
    master_playlist_file = os.path.join(output_dir, f"{output_id}_master.m3u8")
    os.makedirs(os.path.dirname(master_playlist_file), exist_ok=True)
    with open(master_playlist_file, "w") as f:
        f.write('#EXTM3U\n')
        f.write('#EXT-X-VERSION:3\n')
        f.write('#EXT-X-INDEPENDENT-SEGMENTS\n')
        for resolution in resolutions.items():
            f.write("#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION={}x{},CODECS=\"avc1.4d401f,mp4a.40.2\"\n".format(resolution[1]['w'], resolution[1]['h']))
            f.write("{}_{}x{}.m3u8\n".format(output_id, resolution[1]['w'], resolution[1]['h']))
        f.write("#EXT-X-ENDLIST\n")
        # Wait for all threads to finish


    # Save the object instance
    
    upload_to_bucket(output_dir)
    save_object_instance(sender,object_id, output_id, duration)


    
def convert_segment(input_file, output_file, resolution_values, start_time, end_time):
    print(output_file)
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    cmd = ["ffmpeg", "-i", input_file, "-ss", start_time, "-to", end_time, "-vf", "scale={}:{}".format(resolution_values['w'], resolution_values['h']), "-c:v", "libx264", "-c:a", "copy", output_file]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def concatenate_segments(segment_files, output_file):
    concat_file = 'concat.txt'
    with open(concat_file, 'w') as f:
        for segment_file in segment_files:
            f.write("file '{}'\n".format(segment_file))

    cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', output_file]
    subprocess.run(cmd)

def convert_resolution(resolution, input_file, output_dir, output_id, resolutions, duration):
    resolution_values = resolutions[resolution]
    segment_duration = 180
    segments = []
    for i in range(0, int(duration), segment_duration):
        start_time = str(i)
        end_time = str(min(i+segment_duration, duration))
        segment_file = "{}_{}_{}x{}.ts".format(output_id, i//segment_duration, resolution_values['w'], resolution_values['h'])
        output_file = os.path.join(output_dir, segment_file)
        print(segment_file)
        segments.append((input_file, output_file, resolution_values, start_time, end_time))

    # Process segments concurrently using threads
    threads = []
    for segment in segments:
        thread = threading.Thread(target=convert_segment, args=segment)
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    combined_file = os.path.join(output_dir, "{}_{}x{}_combined.ts".format(output_id, resolution_values['w'], resolution_values['h']))
    concatenate_segments([segment[1] for segment in segments], combined_file)

    # Create playlist for this resolution
    playlist_file = os.path.join(output_dir, "{}_{}x{}.m3u8".format(output_id, resolution_values['w'], resolution_values['h']))
    os.makedirs(os.path.dirname(playlist_file), exist_ok=True)
    with open(playlist_file, "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        f.write("#EXT-X-TARGETDURATION:{}\n".format(duration))  # Set the target duration to the segment duration
        f.write("#EXT-X-MEDIA-SEQUENCE:0\n")
        f.write("#EXTINF:{},\n".format(duration))  # Set the total duration as the EXTINF value
        f.write("{}_{}x{}_combined.ts\n".format(output_id, resolution_values['w'], resolution_values['h']))
        f.write("#EXT-X-ENDLIST\n")


def upload_to_bucket(output_dir):
    upload_bucket = client.bucket(GS_UPLOADHLS_BUCKET)
    for filename in os.listdir(output_dir):
        if filename.endswith('.m3u8') or filename.endswith('combined.ts') or filename.endswith('.aac'):
            blob = upload_bucket.blob(os.path.join(filename))
            try:
                print(filename)
                blob.upload_from_filename(os.path.join(output_dir, filename))
            except Exception as e:
                print(f"Error uploading file {filename}: {e}")


def save_object_instance(sender, object_id, output_id, duration):
    if sender == 'movies':
        movie = movies.objects.get(pk=object_id)
        movie.converted_path = f"https://storage.googleapis.com/{GS_UPLOADHLS_BUCKET}/{output_id}_master.m3u8"
        movie.is_converted = True
        movie.save()

        meta_data, created = movieMetaData.objects.get_or_create( movie = object_id)
        meta_data.duration	=duration
        meta_data.save()

    elif sender == 'podcastEpisodes':
        episode = podcastEpisodes.objects.get(pk = object_id)
        episode.converted_path = f"https://storage.googleapis.com/{GS_UPLOADHLS_BUCKET}/{output_id}_master.m3u8"
        episode.is_converted = True
        episode.save()

        meta_data, created = podcastEpisodeMetaData.objects.get_or_create( podcastEpisode = object_id)
        meta_data.duration	=duration
        meta_data.save()

    elif sender == 'seasonEpisodes':
        episode = seasonEpisodes.objects.get(pk = object_id)
        episode.converted_path = f"https://storage.googleapis.com/{GS_UPLOADHLS_BUCKET}/{output_id}_master.m3u8"
        episode.is_converted = True
        episode.save()

        meta_data, created = showEpisodesMetaData.objects.get_or_create( seasonEpisode = object_id)
        meta_data.duration	=duration
        meta_data.save()
    else:
        print("The sender didnt any match any of the models that require a videoConvertion")

