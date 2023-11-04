from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import json

app = Flask(__name__)
api = Api(app)

pictures = []

parser = reqparse.RequestParser()
parser.add_argument('omschrijving')
parser.add_argument('url')


class Picture(Resource):
    def get(self, index):
        if index < len(pictures):
            return pictures[index]
        else:
            return {"message": "Picture not found"}, 404
    
class PicturesList(Resource):
    def get(self):
        return pictures
    
    def post(self):
        args = parser.parse_args()
        print(args)
        pictures.append({'omschrijving': args['omschrijving'],
                         'url': args['url']})
        return pictures[-1], 201

api.add_resource(Picture, '/picture/<int:index>')
api.add_resource(PicturesList, '/pictures')

if __name__ == '__main__':
    app.run(debug=True)