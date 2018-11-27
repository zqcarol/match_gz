from flask import Flask,jsonify,request,make_response,abort
from flask_cors import CORS

from tf_idf_model import Similarity
s=Similarity()
app = Flask(__name__)
CORS(app, resources=r'/*')


#get
@app.route('/sendquery',methods=['GET'])
def get_task():
    if not 'query' in request.args.to_dict():
        abort(404)
    result=s.send_query(request.args.to_dict()['query'])
    return result

#404处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Not found'}),404)

if __name__ == '__main__':
    app.run()
