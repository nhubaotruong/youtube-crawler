import urllib.request, urllib.parse, urllib.error
from database_handler import insert_videos_info

from urllib.request import urlopen as image_downloader
import json
from re import search
from dateutil import parser

class ApiRequestsHandler(object):
    '''
    Abstract class that will handle the requests to the youtube api,
    Subclass should be created for each api version
    '''
    
    def __init__(self, service_client):
        self.service_client = service_client

    def get_uploads_playlist_id(self, channel_id=None, username=None):
        raise NotImplementedError()
    
    def save_videos_info(self, playlist_id):
        raise NotImplementedError()


class ApiV3RequestsHandler(ApiRequestsHandler):
    '''
    The api requests handler for the youtube v3
    '''
    
    def get_uploads_playlist_id(self, channel_id=None, username=None):
        args = {
            'part':'contentDetails'
        }
        
        if channel_id:
            args['id'] = channel_id
        elif username:
            args['forUsername'] = username
        else:
            raise TypeError('Missing the channel_id and the username at least one of them should be provided.')
        
        response = self.service_client.channels().list(**args).execute()
        
        try:
            return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        except:
            raise ValueError("Can't get the videos info of this channel/account")
    
    def save_videos_info(self, playlist_id):
 
        args = {
            'part':'contentDetails',
            'maxResults':50,
            'playlistId':playlist_id
        }

        next_page_token = True

        videos_ids = ''

        while next_page_token:

            videos_ids, next_page_token = self.__save_videos_info_helper(args)
            
            self.__store_videos_info(videos_ids)
            
            args['pageToken'] = next_page_token
        
        
        return videos_ids

    def __save_videos_info_helper(self, args):

        videos_ids = ''

        response = self.service_client.playlistItems().list(**args).execute()

        for i in range(len(response['items'])):
            video_id = response['items'][i]['contentDetails']['videoId']

            if i != len(response['items'])-1:
                video_id += ','
            
            videos_ids += video_id
        
        return videos_ids, response.get('nextPageToken', False)
    
    def __store_videos_info(self, videos_ids):
        
        args = {
            'part': 'snippet,contentDetails,statistics',
            'maxResults': 50,
            'id': videos_ids
        }

        videos = []
        
        # needed = []
        response = self.service_client.videos().list(**args).execute()
        
        for i in response['items']:

            # thumbnail = i['snippet']['thumbnails']['default']['url']
            # image = i['snippet']['thumbnails']['high']['url']

            # thumbnail_url = 'images//'+i['id']+'-thumb'+'.jpg'
            # image_url = 'images//'+i['id']+'.jpg'

            # image_downloader.retrieve(thumbnail, thumbnail_url)
            # image_downloader.retrieve(image, image_url)

            url = 'https://www.youtube.com/watch?v=' + i['id']
            title = i['snippet']['title']
            description = i['snippet']['description']
            duration = i['contentDetails']['duration']
            publishedDate = i['snippet']['publishedAt']
            parsed_time = parser.parse(publishedDate)
            viewCount = i['statistics']['viewCount']
            video = (title, description, duration, parsed_time, viewCount, url)
            
            # try:
            #     name = search('(.+) \|', title).group(1)
            # except Exception:
            #     name = ''

            # try:
            #     nguyen_lieu = description.partition("NGUYÊN LIỆU:")[2].partition("#")[0]
            # except Exception:
            #     nguyen_lieu = ''

            # needer = {
            #     'time': parsed_time,
            #     'name': name,
            #     'nguyen_lieu': nguyen_lieu
            # }
            # needed.append(needer)
            videos.append(video)
        
        insert_videos_info(videos)
        # with open('output.json', mode='w', encoding='utf-8') as file:
        #     json.dump(needed, file)