from flask import Flask,jsonify,request,make_response,abort


from tf_idf_model import Similarity
s=Similarity()
app = Flask(__name__)

MY_URL = '/everything/api/v1/'
hello='今天天气真好呀'
not_hello = '为什么今天天气不好呀'

#get
@app.route(MY_URL + 'tasks/get/',methods=['GET'])
def get_task():
    if not 'query' in request.args.to_dict():
        abort(404)
    # print(request.args.to_dict()['query'])  #
    result=s.send_query(request.args.to_dict()['query'])
    return result


#404处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Not found'}),404)

if __name__ == '__main__':
    app.run()
