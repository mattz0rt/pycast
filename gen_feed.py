from feedgen.feed import FeedGenerator
from mutagen.easyid3 import EasyID3
from google.cloud import storage
from glob import glob
import urlparse
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), 'API Project-dd4536b2c838.json')

def upload_blob(source_file_name, bucket_name='pycast', destination_blob_name=None):
    if destination_blob_name is None:
        destination_blob_name = os.path.basename(source_file_name)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    if blob.exists():
        return blob.public_url

    print("Uploading {} to {}".format(source_file_name, destination_blob_name))
    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

    blob.make_public()
    
    return blob.public_url

def sorted_ls(path):
    mtime = lambda f: os.stat(f).st_mtime
    return list(sorted(glob(path), key=mtime, reverse=True))

if __name__ == '__main__':
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    fg.title('mattz0rt\'s personal feed')
    fg.link(href='https://github.com/mattz0rt/pycast', rel='alternate')
    fg.description('A personal feed')
    fg.podcast.itunes_category('Technology', 'Podcasting')
    
    for mp3 in sorted_ls('audio/*.mp3'):
        mp3_url = upload_blob(mp3)
        fe = fg.add_entry()
        mp3_meta = EasyID3(mp3)
        fe.id(mp3_url)
        fe.title(mp3_meta['title'][0])
        fe.description('by ' + mp3_meta['artist'][0])
        fe.link(href=mp3_url)
        fe.enclosure(mp3_url, 0, 'audio/mpeg')
    
    fg.rss_str(pretty=True)
    fg.rss_file('podcast.xml')
