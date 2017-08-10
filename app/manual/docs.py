from . import manual
#from datetime import datetime
#from pytz import timezone
from flask import render_template

#tzchina = timezone('Asia/Shanghai')
#utc = timezone('UTC')


@manual.route('/')
def docs():
    return render_template('doc.html')
