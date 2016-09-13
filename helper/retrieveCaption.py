import xml.etree.ElementTree as ET

# Edge cases: 

def returnTime(time):
    timearr = time.split(':')
    hour = int(timearr[0])*60*60
    mins = int(timearr[1])*60
    secs = int(float(timearr[2]))
    totalsecs = hour+mins+secs
    return totalsecs

# Recieved the time stamp of 500
in_time = 80

# Get everything from 490 to 510
in_time_offset = 20

# Ensure we are never starting at a negative time
in_time_start = max(in_time - in_time_offset,0)

in_time_end = in_time + in_time_offset

tree = ET.parse('_wKUEOeAnFI')
root = tree.getroot()
div = root[1][0]

# Total sentences
total_p = len(div.findall("./"))

split_p_init = total_p/2

split_p_btime = returnTime(div[split_p_init].get('begin'))
split_p_etime = returnTime(div[split_p_init].get('end'))
split_p_bindex = split_p_init

# Start Index: Stop if we've reach the first p element
while(split_p_bindex != 0):
    if(in_time_start >= split_p_btime and in_time_start <= split_p_etime):
        break;
    elif (in_time_start < split_p_btime):
        split_p_bindex = max(split_p_bindex - split_p_bindex/2,0)
        split_p_btime = returnTime(div[split_p_bindex].get('begin'))
        split_p_etime = returnTime(div[split_p_bindex].get('end'))
    elif (in_time_start > split_p_etime):
        split_p_bindex = min(split_p_bindex + split_p_bindex/2, total_p)
        split_p_btime = returnTime(div[split_p_bindex].get('begin'))
        split_p_etime = returnTime(div[split_p_bindex].get('end'))

split_p_eindex = split_p_init
split_p_btime = returnTime(div[split_p_init].get('begin'))
split_p_etime = returnTime(div[split_p_init].get('end'))

# End Index: Stop if we've reached the last p element
while(split_p_eindex != total_p):
    if(in_time_end >= split_p_btime and in_time_end <= split_p_etime):
        break;
        #save sentence
    elif (in_time_end < split_p_btime):
        split_p_eindex = max(split_p_eindex - split_p_eindex/2,0)
        split_p_btime = returnTime(div[split_p_eindex].get('begin'))
        split_p_etime = returnTime(div[split_p_eindex].get('end'))
    elif (in_time_end > split_p_etime):
        split_p_eindex = min(split_p_eindex + split_p_eindex/2, total_p)
        split_p_btime = returnTime(div[split_p_eindex].get('begin'))
        split_p_etime = returnTime(div[split_p_eindex].get('end'))


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

#print note_str
