from flask import Flask
from flask import request #请求参数
from flask import render_template #引入模板
from flask import redirect, url_for
import os, json, shutil
from traj_processor import *
from utils import create_circle
from flask_dropzone import Dropzone

basedir = os.path.abspath(os.path.dirname(__file__))
processor = None
app = Flask(__name__)

app.config.update(
    UPLOADED_PATH=os.path.join(basedir, 'uploads'),
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_TYPE='default',
    DROPZONE_MAX_FILE_SIZE=300,
    DROPZONE_MAX_FILES=300,
    DROPZONE_PARALLEL_UPLOADS=3,  # set parallel amount
    DROPZONE_UPLOAD_MULTIPLE=True,  # enable upload multiple
)
dropzone = Dropzone(app)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')


@app.route('/get_files', methods=['POST', 'GET'])
def get_files():
    global processor
    path = os.path.join(app.config['UPLOADED_PATH'])
    processor = HandledFilesProcessor(path)
    # print(path)
    trajs = processor.get_whole_traj()
    coords = processor.get_whole_points()
    lon, lat = processor.get_center()
    return json.dumps({"lines": trajs,
                       'points': coords,
                       "center": [lon, lat]},
                      separators=(',', ': '))


@app.route('/to_semantic', methods=['POST', 'GET'])
def to_semantic_traj():
    print("begin semantic")
    # home_points, work_points = processor.generate_homeAngWork_place_points()
    # (home_center, home_radius) = create_circle(home_points)
    # (work_center, work_radius) = create_circle(work_points)
    semantic_traj = processor.get_main_traj_semantic()
    print("end semantic")
    return json.dumps({"semantic_traj": semantic_traj}, separators=(',', ': '))
    # return json.dumps({"home_points": home_points,
    #                    "work_points": work_points,
    #                    "home_circle": [home_center, home_radius],
    #                    "work_circle": [work_center, work_radius]},
    #                   separators=(',', ': '))



@app.route('/traj_cluster', methods=['POST', 'GET'])
def traj_cluster():
    print('begin cluster')
    clusters = processor.generate_traj_cluster()
    print(clusters)
    return json.dumps({"cluster": clusters}, separators=(',', ': '))


@app.route('/get_stop_points', methods=['POST', 'GET'])
def get_stop_points():
    stop_points = processor.get_stop_points()
    print(stop_points)
    return json.dumps({"stop_points": stop_points}, separators=(',', ': '))


@app.route('/generate_POI', methods=['POST', 'GET'])
def generate_POI():
    print('POI')
    cluster_of_POI = processor.generate_POI()
    radius_ = []
    centers = []
    for key in cluster_of_POI.keys():
        (center, radius) = create_circle(cluster_of_POI[key])
        centers.append(center)
        radius_.append(radius)
    interest = processor.get_area_interest()
    print("int:",interest)
    return json.dumps({"cluster": cluster_of_POI,
                       "centers": centers,
                       "radius": radius_,
                       "interest": interest}, separators=(',', ': '))


# @app.route('/analysis', methods=['POST', 'GET'])
# def analysis():
#     print("analysis")
#     return render_template('analysis.html')


@app.before_first_request
def cleanup():
    # global processor
    print("here")
    shutil.rmtree(app.config['UPLOADED_PATH'])
    os.mkdir(app.config['UPLOADED_PATH'])
    # processor = HandledFilesProcessor("C:/Users/cak/PycharmProjects/flaskProject1/uploads")


if __name__ == '__main__':
    app.run(debug=True)
