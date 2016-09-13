# Use this to strip the unicode chars
import HTMLParser
parser = HTMLParser.HTMLParser()
# Use this to strip the <br> chars
import re
with open('output.en.ttml') as infile, open('pro-output.ttml', 'w') as outfile:
    for line in infile:
        line = re.sub('<br.*?/>', ' ', line)
        outfile.write(parser.unescape(line))
