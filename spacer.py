##########################################
# Add spacers to your home screen with   #
# Pythonista.                            #
# It may help to enable 'Reduce Motion'  #
# in Settings > General > Accessibility. #
# I have it turned on anyway.            #
#                                        #
# To use this script, you need to first  #
# take a screenshot of an empty home     #
# screen, by tap-holding an icon         #
# ("jiggle mode") and going to the very  #
# last page, then taking a screenshot.   #
# Then go back to Pythonista and run     #
# spacer.py.                             #
#                                        #
# iphone 5/5s only for now, but it can   #
# be easily adapted by adjusting these   #
# variables. 4/4s may also work, but you #
# might need to change 'rows' to 4.      #
##########################################
size = 120
startpos = (32, 50)
diff = (152, 176)
cols, rows = 4, 5


from ui import Image as UIImage
from PIL import Image as PILImage
import io          # image conversion
import photos      # get screenshot
import webbrowser  # open page
import threading   # delay open page
import bottle      # web server
import base64      # encode data
from ui import get_screen_size
from scene import get_screen_scale

scale = get_screen_scale()
screensize = get_screen_size()

positions = [[(startpos[0] + diff[0]*col,
               startpos[1] + diff[1]*row)
              for col in range(cols)]
             for row in range(rows)]

def getscreenshot():
	data = photos.pick_image(raw_data=True)
	return UIImage.from_data(data)
	
def geticon(row, column):
	p = positions[row][column]
	with io.BytesIO(screen.to_png()) as f:
		pilscreen = PILImage.open(f)
		pilscreen.load()
	pilicon = pilscreen.crop((p[0], p[1], p[0]+size, p[1]+size))
	with io.BytesIO() as f:
		pilicon.save(f, 'PNG')
		uiicon = UIImage.from_data(f.getvalue())
	return uiicon

pagetemplate = '''
<!DOCTYPE html>
<html>
<head>
<script>
if (window.navigator.standalone) {
	location.href = "pythonista://";
}
</script>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="apple-touch-icon-precomposed" href="%s">
<title>&zwj;</title>
<style>
a {
	display:block;
	position:absolute;
	border-radius:12px;
	background:rgba(255,0,0,0.5);
	width:%dpx;
	height:%dpx;
}

.chosen {
	background:rgba(0,0,255,0.5);
}

#background {
	background: url(http://localhost:8080/screen.png);
	background-size:100%%;
	height:%dpx;
}

body {
	margin:0;
}
</style>
</head>
<body>
<div id=background></div>
%s
</body>
</html>
'''

@bottle.route('/<row:int>/<column:int>')
def page(row, column):
	tagtemplate = '''
	<a
	class="{aclass}"
	href="http://localhost:8080/{row}/{col}"
	style="left:{x}px;top:{y}px;"></a>
	'''
	tags = []
	for r in range(rows):
		for c, pos in enumerate(positions[r]):
			x, y = (pos[0]/2, pos[1]/2)
			aclass = 'chosen' if r == row and c == column else ''
			tags.append(tagtemplate.format(
				x=x,
				y=y,
				row=r,
				col=c,
				aclass=aclass))
	tagsstr = ''.join(tags)
	iconpng = geticon(row, column).to_png()
	iconurl = 'data:image/png;base64,' + base64.b64encode(iconpng)
	
	html = pagetemplate % (iconurl, size/scale, size/scale, screensize[1], tagsstr)
	redirecturl = 'data:text/html;base64,' + base64.b64encode(html)
	bottle.redirect(redirecturl)

@bottle.route('/screen.png')
def screenpng():
	bottle.response.set_header('Content-Type', 'image/png')
	return screen.to_png()


screen = getscreenshot()
	
threading.Timer(1, webbrowser.open, ('safari-http://localhost:8080/0/0',)).start()

bottle.run(host='0.0.0.0', debug=False)
	
