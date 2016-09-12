import HTMLParser
parser = HTMLParser.HTMLParser()
with open('output.en.ttml') as infile, open('pro-output.ttml', 'w') as outfile:
    for line in infile:
        outfile.write(parser.unescape(line))
