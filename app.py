from flask import Flask
app = Flask(__name__)
from flask import request


@app.route('/', methods=['GET','POST'])
def json():
    app.logger.debug("JSON received...")
    app.logger.debug(request.json)

    if request.json:
        mydata = request.json

        return "name is = %s\n" % mydata.get("name")
    else:
        return "no json received"

if __name__ == '__main__':
    app.run()

