from __future__ import unicode_literals
import youtube_dl
import re
import xml.etree.ElementTree as ET
import os.path


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print msg

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

YDL_OPTS = {
    'writeautomaticsub': True,
    'writesubtitles': True,
    'skip_download': True,
    'subtitlesformat': 'ttml',
    'outtmpl': '/tmp/output',
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

def preprocess_and_output(video_id):
    outfile_name = str(video_id)
    # TODO(shelbyt): ENLANG
    with open('/tmp/output.en.ttml') as infile, open('/tmp/'+outfile_name, 'w') as outfile:
        for line in infile:
            # Remove any BR tags in the sentences, messed up XML parsing
            # if they are not removed
            line = re.sub('<br.*?/>', ' ', line)
            outfile.write(line)
    # TODO(shelbyt): ENLANG
    if os.path.isfile("/tmp/output.en.ttml"):
        os.remove("/tmp/output.en.ttml")

def download_subs(video_id,context):
    print("Time remaining (MS):", context.get_remaining_time_in_millis())
    with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
        ydl.download(['http://www.youtube.com/watch?v='+str(video_id)])
    print("Time remaining (MS):", context.get_remaining_time_in_millis())
    # TODO(shelbyt): ENLANG
    # If we have sucessfully downloaded a subtitle begin to process it
    if os.path.isfile("/tmp/output.en.ttml"):
        print "Subtitles exist"
        preprocess_and_output(video_id)
        return 0
    else:
        print "Subtitles DONOT exist"
        # If the subtitle does not exist, return error code
        return -1

def return_sentences(video_id, in_time, in_time_offset):
    #TODO(shelbyt): EDGE CASES: Sentences one after an anther have
    #the same time stamp. Print both

    # Ensure that the time we're working with is an int
    # print type(in_time)
    in_time = int(in_time)
    # TODO(shelbyt): Dangerous to parse local file in server?
    tree = ET.parse('/tmp/'+video_id)
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

    # Start Index: Stop if we've reach the first p element
    # Ensure we are never starting at a negative time
    in_time_start = max(in_time - in_time_offset, 0)


    #TODO:(shelbyt): This is a hack to make sure we don't oscillate between
    # two indexes i.e. id-LHAywHmItKM @ time 0:00
    prev_index = -999
    while split_p_bindex != 0:
        if split_p_bindex is prev_index:
            break
        else:
            prev_index = split_p_bindex
        if in_time_start == 0:
            split_p_bindex = in_time_start
            break
        if in_time_start >= split_p_btime and in_time_start <= split_p_etime:
            break
        elif in_time_start < split_p_btime:
            end_index = split_p_bindex
            split_p_bindex = max(split_p_bindex -
                    abs(start_index - end_index)/2, 0)
            split_p_btime = returnTime(div[split_p_bindex].get('begin'))
            split_p_etime = returnTime(div[split_p_bindex].get('end'))
        elif in_time_start > split_p_etime:
            start_index = split_p_bindex
            split_p_bindex = min(split_p_bindex +
                    abs(start_index - end_index)/2, total_p)
            split_p_btime = returnTime(div[split_p_bindex].get('begin'))
            split_p_etime = returnTime(div[split_p_bindex].get('end'))
        #print split_p_bindex
    start_index = 0
    end_index = total_p

    split_p_eindex = split_p_init
    split_p_btime = returnTime(div[split_p_init].get('begin'))
    split_p_etime = returnTime(div[split_p_init].get('end'))
    # Ensure we are never off the edge of the video
    in_time_end = min(in_time + in_time_offset,
            returnTime(div[total_p -1].get('end')))
    # End Index: Stop if we've reached the last p element

    #TODO:(shelbyt): This is a hack to make sure we don't oscillate between
    # two indexes i.e. id-LHAywHmItKM @ time 0:00
    prev_index = -999
    while split_p_eindex != total_p:
        if split_p_eindex is prev_index:
            break
        else:
            prev_index = split_p_eindex
        if in_time_end == returnTime(div[total_p -1].get('end')):
            split_p_eindex = total_p - 1
            break
        if in_time_end >= split_p_btime and in_time_end <= split_p_etime:
            break
        elif in_time_end < split_p_btime:
            end_index = split_p_eindex
            split_p_eindex = max(split_p_eindex -
                   abs(start_index - end_index)/2, 0)
            split_p_btime = returnTime(div[split_p_eindex].get('begin'))
            split_p_etime = returnTime(div[split_p_eindex].get('end'))
        elif in_time_end > split_p_etime:
            start_index = split_p_eindex
            split_p_eindex = min(split_p_eindex +
                   abs(start_index - end_index)/2, total_p)
            split_p_btime = returnTime(div[split_p_eindex].get('begin'))
            split_p_etime = returnTime(div[split_p_eindex].get('end'))

    note_str = ""
    # Should be ok vs. fall off the end because last index
    # is not included in range. Still may be bad style
    for sentence in range(split_p_bindex, split_p_eindex+1):# why +1
        # Need to check if it a NoneType because some lines in the
        # transcript have only <p> elements with no content. This
        # causes a typeconversion error between str+NonType
        if div[sentence].text is None:
            continue
        sentence_enc = div[sentence].text.decode('unicode_escape').encode('ascii', 'ignore')
        if sentence == split_p_eindex:
            note_str += sentence_enc;
        else:
            note_str += sentence_enc + " "

    #print "DONE"
    return note_str
    #print note_str

def lambda_handler(event, context):
    # TODO(shelbyt): Lock the file? And make sure that this
    # is actually a good way to store and check for file existing.
    print event["id"]
    print event["time"]
    if download_subs(event["id"],context) == 0:
        return return_sentences(event["id"], event["time"], 10)
    else:
        return "Notes Unavailable"


