from flask import Flask
from flask_restful import Resource, Api, reqparse
from decouple import config
from flask_mysqldb import MySQL
from os import getenv

app = Flask(__name__)

app.config['SECRET_KEY'] = getenv('SECRET_KEY', config('SECRET_KEY'))
app.config['MYSQL_HOST'] = getenv('DB_HOST', config('DB_HOST'))
app.config['MYSQL_USER'] = getenv('DB_USER', config('DB_USER'))
app.config['MYSQL_PASSWORD'] = getenv('DB_PASSWORD', config('DB_PASSWORD'))
app.config['MYSQL_DB'] = getenv('DB_NAME', config('DB_NAME'))
mysql = MySQL()
mysql.init_app(app)

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, help='Rate to charge for this resource')
parser.add_argument('password', type=str, help='Rate to charge for this resource')
parser.add_argument('admin', type=bool, help='Rate to charge for this resource')


class User(Resource):
    def get(self, user_id):
        cur = mysql.connection.cursor()
        sql = '''SELECT * FROM users WHERE id = %s'''
        cur.execute(sql, (user_id,))
        row = cur.fetchone()

        if row is not None:
            result = {'user': row[1], 'admin': row[3]}
        else:
            result = {'Error': 'No user with that id'}
        cur.close()
        return result

    def put(self, user_id):
        args = parser.parse_args()
        if 'name' in args and 'password' in args:
            cur = mysql.connection.cursor()
            if 'admin' in args:
                admin = args['admin']
                sql = '''UPDATE users set username = %s, password = %s, admin = %s WHERE id %s'''
                cur.execute(sql, (args['name'], args['password'], admin, user_id))
            else:
                sql = '''UPDATE users set username = %s, password = %s WHERE id %s'''
                cur.execute(sql, (args['name'], args['password'], user_id))
            mysql.connection.commit()
            cur.close()
            if cur.rowcount:
                result = {"Success": "Updated user with id {}.".format(user_id)}
            else:
                result = {"Error": "Couldn't find or couldn't delete user with id {}.".format(user_id)}
        else:
            result = {'Error': "Not enough parameters to create a user"}
        return result

    def delete(self, user_id):
        cur = mysql.connection.cursor()
        sql = '''DELETE FROM users WHERE id = %s'''
        cur.execute(sql, (user_id,))
        mysql.connection.commit()
        cur.close()
        if cur.rowcount:
            return {"Success": "Deleted user with id {}.".format(user_id)}
        else:
            return {"Error": "Couldn't find or couldn't delete user with id {}.".format(user_id)}


class Users(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM users''')
        rows = cur.fetchall()
        cur.close()
        if rows is not None:
            result = []
            for row in rows:
                result.append({'name': row[1], 'id': row[0], 'admin': row[3]})
        else:
            result = {'Error': 'There are no users'}
        return result

    def post(self):
        args = parser.parse_args()
        if 'name' in args and 'password' in args:
            admin = False
            if 'admin' in args:
                admin = args['admin']
            cur = mysql.connection.cursor()
            sql = '''INSERT INTO users (username, password, admin) VALUES (%s, %s, %s)'''
            cur.execute(sql, (args['name'], args['password'], admin,))
            mysql.connection.commit()
            cur.close()
            result = {'Success': 'User inserted'}
        else:
            result = {'Error': "Not enough parameters to create a user"}
        return result


@app.route('/')
def hello_world():
    return 'Hello, use API please!'


api.add_resource(Users, '/users')
api.add_resource(User, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run()
