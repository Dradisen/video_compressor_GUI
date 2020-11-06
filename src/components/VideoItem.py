import subprocess, json

from .CompressStatus import CompressStatus

class VideoItem():
    STATUS = {
        CompressStatus.WAIT: 'В ожидании',
        CompressStatus.PROCESS: 'Сжатие',
        CompressStatus.COMPLETE: 'Завершено!'}
    FFPROBE_SETTINGS = [
        '-v', 'error', 
        '-show_entries', 
        'stream=width,height,codec_name,profile'+\
            ': format=filename,bit_rate,size,duration'+\
            ': format_tags=title',
        '-print_format', 'json']
    
    def __init__(self, path=None):
        print("PATH: ", path)
        if(path is not None):
            video = subprocess.check_output([
                    'ffprobe', '-i', path, *self.FFPROBE_SETTINGS])
            video = json.loads(video)
            self.__video = {**video['streams'][0], **video['format']}
            self.__video['status'] = self.STATUS[CompressStatus.WAIT]
            self.__video['progress'] = 0
        
    def getIDitem(self):
        return self.__video['id']
    
    def getResolution(self):
        return '{}x{}'.format(self.__video['width'], self.__video['height'])

    def getProgress(self):
        return self.__video['progress']
    
    def getFilename(self):
        if not 'title' in self.__video['tags']:
            self.__video['title'] = self.__video['filename'].split('/').pop()
        else:
            self.__video['title'] = self.__video['tags']['title']        
        return self.__video['title']
    
    def getPathFile(self):
        return self.__video['filename']
        
    def getSize(self):
        return self.__format_size_file(self.__video['size'])
    
    def getSizeof(self):
        return self.__video['size']
    
    def getDuration(self):
        return self.__format_video_time(self.__video['duration'])
    
    def getStatusCompress(self):
        return self.__video['status']
    
    def getStatus(self):
        return self.__video['status']
    
    def setStatus(self, status:CompressStatus):
        self.__video['status'] = self.STATUS[status]
    
    def setIDitem(self, id):
        self.__video['id'] = id
        
    def setProgress(self, value):
        self.__video['progress'] = value
    
    def __format_size_file(self, bytes):
        suffix_size = {'M' : 1024 ** 2, 'G' :  1024 ** 3}
        
        return "{} Мб".format(round(int(bytes) // suffix_size['M'], 1))\
            if int(bytes) // suffix_size['G'] == 0 \
            else "{} Гб".format(round(int(bytes) // suffix_size['G'], 1))
            
    def __format_video_time(self, seconds):
        return "{} мин".format(round(float(seconds) / 60, 1))