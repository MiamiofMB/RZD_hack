import os
from flask import Flask, flash, request, redirect, send_file, render_template,url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath('DATA2')
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

config = []


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global config
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            config.append(filename)
            return redirect(url_for("return_pb"))
    return render_template('main_page.html')



@app.route('/return_pb',methods=['get','post'])
def return_pb():
    return render_template('result.html')
#короче редирект после получения материала на






if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345, debug=False)
