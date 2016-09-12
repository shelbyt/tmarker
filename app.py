from __future__ import unicode_literals
from flask import Flask
app = Flask(__name__)
from flask import request
import youtube_dl
import HTMLParser
parser = HTMLParser.HTMLParser()



class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
    'writeautomaticsub': True,
    'skip_download': True,
    'subtitlesformat': 'ttml',
    'outtmpl': 'output',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

def preProcessAndOutput(video_id):
    outfile_name = str(video_id)
    with open('output.en.ttml') as infile, open(outfile_name,'w') as outfile:
        for line in infile:
            outfile.write(parser.unescape(line))

def downloadSubs(video_id):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['http://www.youtube.com/watch?v='+str(video_id)])
        preProcessAndOutput(video_id)

@app.route('/', methods=['GET','POST'])
def json():
    app.logger.debug("JSON received...")
    app.logger.debug(request.json)

    if request.json:
        mydata = request.json
        downloadSubs(mydata.get("id"))
        return "name is = %s\n" % mydata.get("name")
        return "ytid is = %s\n" % mydata.get("id")
    else:
        return "no json received"

if __name__ == '__main__':
    app.run()

