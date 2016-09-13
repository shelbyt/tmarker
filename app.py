from __future__ import unicode_literals
from flask import Flask
app = Flask(__name__)
from flask import request
import youtube_dl
import HTMLParser
import re
import xml.etree.ElementTree as ET

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

def returnTime(time):
    timearr = time.split(':')
    hour = int(timearr[0])*60*60
    mins = int(timearr[1])*60
    secs = int(float(timearr[2]))
    totalsecs = hour+mins+secs
    return totalsecs

def preProcessAndOutput(video_id):
    outfile_name = str(video_id)
    with open('output.en.ttml') as infile, open(outfile_name,'w') as outfile:
        for line in infile:
            line = re.sub('<br.*?/>', ' ', line)
            outfile.write(parser.unescape(line))

def downloadSubs(video_id):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['http://www.youtube.com/watch?v='+str(video_id)])
        preProcessAndOutput(video_id)

def returnSentences(video_id, in_time, in_time_offset):
    #TODO(shelbyt): EDGE CASES: Sentences one after an anther have
    #the same time stamp. Print both

    # Ensure that the time we're working with is an int
    #print in_time
    #in_time = int(in_time)
    print type(in_time)
    in_time = int(in_time)

    # Ensure we are never starting at a negative time
    in_time_start = max(in_time - in_time_offset,0)
    
    in_time_end = in_time + in_time_offset
   
    # TODO(shelbyt): Dangerous to parse local file in server?
    tree = ET.parse(video_id)
    root = tree.getroot()
    div = root[1][0]
    
    # Total sentences
    total_p = len(div.findall("./"))
    
    split_p_init = total_p/2
    
    split_p_btime = returnTime(div[split_p_init].get('begin'))
    split_p_etime = returnTime(div[split_p_init].get('end'))
    split_p_bindex = split_p_init

    start_index = 0
    end_index = total_p
    mid_index = total_p/2

    print split_p_btime
    print split_p_etime
    print in_time
    print split_p_bindex
    #return
    
    # TODO(shelbyt): Any way to avoid having to do the bsearch twice?
    # Start Index: Stop if we've reach the first p element
    while(split_p_bindex != 0):
        #print str(in_time_start) + " >= " + str(split_p_btime) + " :: " + str(in_time_start) + " <= " + str(split_p_etime)
        if(in_time_start >= split_p_btime and in_time_start <= split_p_etime):
            break;
        elif (in_time_start < split_p_btime):
            end_index = split_p_bindex
            split_p_bindex = max(split_p_bindex - abs(start_index - end_index)/2,0)
            split_p_btime = returnTime(div[split_p_bindex].get('begin'))
            split_p_etime = returnTime(div[split_p_bindex].get('end'))
        elif (in_time_start > split_p_etime):
            start_index = split_p_bindex
            split_p_bindex = min(split_p_bindex + abs(start_index - end_index)/2, total_p)
            split_p_btime = returnTime(div[split_p_bindex].get('begin'))
            split_p_etime = returnTime(div[split_p_bindex].get('end'))
        #print split_p_bindex
   
    #print "next"
    start_index = 0
    end_index = total_p
    mid_index = total_p/2

    split_p_eindex = split_p_init
    split_p_btime = returnTime(div[split_p_init].get('begin'))
    split_p_etime = returnTime(div[split_p_init].get('end'))
 
    # End Index: Stop if we've reached the last p element
    while(split_p_eindex != total_p):
        #print str(in_time_end) + " >= " + str(split_p_btime) + " :: " + str(in_time_end) + " <= " + str(split_p_etime)
        if(in_time_end >= split_p_btime and in_time_end <= split_p_etime):
            break;
        elif (in_time_end < split_p_btime):
            end_index = split_p_eindex
            split_p_eindex = max(split_p_eindex - abs(start_index - end_index)/2,0)
            split_p_btime = returnTime(div[split_p_eindex].get('begin'))
            split_p_etime = returnTime(div[split_p_eindex].get('end'))
        elif (in_time_end > split_p_etime):
            start_index = split_p_eindex
            split_p_eindex = min(split_p_eindex + abs(start_index - end_index)/2, total_p)
            split_p_btime = returnTime(div[split_p_eindex].get('begin'))
            split_p_etime = returnTime(div[split_p_eindex].get('end'))
        print split_p_eindex
    
    #print "Begin index is " + str(split_p_bindex)
    #print "End index is " + str(split_p_eindex)
    
    note_str = ""
    # Should be ok vs. fall off the end because last index
    # is not included in range. Still may be bad style
    for sentence in range(split_p_bindex,split_p_eindex+1):
        if(sentence == split_p_eindex):
            note_str += div[sentence].text
        else:
            note_str += div[sentence].text + "\n"

    #print "DONE"
    return note_str
    #print note_str


@app.route('/', methods=['GET','POST'])
def json():
    app.logger.debug("JSON received...")
    app.logger.debug(request.json)

    if request.json:
        mydata = request.json
        downloadSubs(mydata.get("id"))
        #print type(mydata.get("time"))
        #print type(mydata.get("id"))
        print(type(mydata.get("time")))
        return returnSentences(mydata.get("id"), mydata.get("time"), 20)
        #return "DATA"
    else:
        return "no json received"

if __name__ == '__main__':
    app.run()

