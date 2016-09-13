import xml.etree.ElementTree as ET

# Read the xml file
tree = ET.parse('_wKUEOeAnFI')

# Get the elments
root = tree.getroot()

# SAMPLE TTML FILE
# <tt xmlns="http://www.w3.org/ns/ttml" xmlns:ttm="http://www.w3.org/ns/ttml#metadata" xmlns:tts="http://www.w3.org/ns/ttml#styling" xmlns:ttp="http://www.w3.org/ns/ttml#parameter" xml:lang="en" ttp:profile="http://www.w3.org/TR/profile/sdp-us">
# <head>
# <styling>
# <style xml:id="s1" tts:textAlign="center" tts:extent="90% 90%" tts:origin="5% 5%" tts:displayAlign="after"/>
# <style xml:id="s2" tts:fontSize=".72c" tts:backgroundColor="black" tts:color="white"/>
# </styling>
# <layout>
# <region xml:id="r1" style="s1"/>
# </layout>
# </head>
# <body region="r1">
# <div>
# <p begin="00:00:00.220" end="00:00:15.430" style="s2">
# we really emphasize the ways in which
# <br/>
# strategies and ongoing iterative process
# </p>


# Get the 0th child of the 1st child of root
# gets the div element in the ttml file and every
# child is a <p> element
# root[0] = head
# root[1] = body
# root[1][0] = div

root = root[1][0]
print root

# Print all the paragraph elements
for child in root:
    print child

# print {'begin': '00:00:28.210', 'end': '00:00:32.380', 'style': 's2'}
print root[4].attrib

# print text in between elements i.e. 'of the most basic level strategy is just'
print root[4].text

# print contents in begin id of <p> tag i.e. '00:00:28.210'
print root[4].get('begin')
