from flask import Flask, jsonify, request, session
from flask_restful import Resource, Api, reqparse
from decouple import config
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from os import getenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

api = Api(app)

app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['MYSQL_HOST'] = getenv('DB_HOST', config('DB_HOST'))
app.config['MYSQL_USER'] = getenv('DB_USER', config('DB_USER'))
app.config['MYSQL_PASSWORD'] = getenv('DB_PASSWORD', config('DB_PASSWORD'))
app.config['MYSQL_DB'] = getenv('DB_NAME', config('DB_NAME'))
mysql = MySQL()
mysql.init_app(app)

app.config['SECRET_KEY'] = getenv('SECRET_KEY', config('SECRET_KEY'))
jwt = JWTManager(app)

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('admin', type=bool)
parser.add_argument('email', type=str)


class User(Resource):
    def get(self, user_id):
        cur = mysql.connection.cursor()
        sql = '''SELECT * FROM users WHERE id = %s'''
        cur.execute(sql, (user_id,))
        row = cur.fetchone()

        if row is not None:
            return jsonify({'username': row[1], 'admin': row[3], 'email': row[4]})
        else:
            response = jsonify({'Error': 'No user with that id'})
            response.status_code = 404
            return

    @jwt_required
    def put(self, user_id):
        if session.get('admin') == 0 and user_id != session.get('id'):
            response = jsonify({'err': 'Only admin can create new users'})
            response.code = 403
            return response

        args = parser.parse_args()
        if 'password' in args and 'email' in args:
            cur = mysql.connection.cursor()
            if 'admin' in args:
                admin = args['admin']
                sql = '''UPDATE users set password = %s, admin = %s, email = %s WHERE id %s'''
                cur.execute(sql, (args['password'], admin, args['email'], user_id))
            else:
                sql = '''UPDATE users set password = %s WHERE id %s'''
                cur.execute(sql, (args['password'], args['email'], user_id))
            mysql.connection.commit()
            cur.close()
            if cur.rowcount:
                return jsonify({"Success": "Updated user with id {}.".format(user_id)}), 200
            else:
                return({"Error": "Couldn't find or couldn't delete user with id {}.".format(user_id)}), 400
        else:
            return jsonify({'Error': "Not enough parameters to create a user"}), 400

    @jwt_required
    def delete(self, user_id):
        #only admin should be able to delete user
        if session.get('admin') == 0:
            response = jsonify({'err': 'Only admin can create new users'})
            response.code = 403
            return response

        cur = mysql.connection.cursor()
        sql = '''DELETE FROM users WHERE id = %s'''
        cur.execute(sql, (user_id,))
        mysql.connection.commit()
        cur.close()
        if cur.rowcount:
            return jsonify({"msg": "Deleted user with id {}.".format(user_id)}), 204
        else:
            return jsonify({"err": "Couldn't find or couldn't delete user with id {}.".format(user_id)}), 404


class Users(Resource):
    def get(self):
        if request.args.get('username'):
            return self.getByUsername(request.args.get('username'))
        elif request.args.get('email'):
            return self.getByUsername(request.args.get('email'))

        cur = mysql.connection.cursor()
        sql = '''SELECT * FROM users'''
        if request.args.get('admins'):
            sql += ''' WHERE admin = True'''
        if request.args.get('limit'):
            print(request.args.get('limit'))
            sql += ''' LIMIT ''' + request.args.get('limit')
        if request.args.get('sort'):
            sql += ''' ORDER BY ''' + request.args.get('sort')

        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        if rows is not None:
            result = []
            for row in rows:
                result.append({'username': row[1], 'id': row[0], 'admin': row[3], 'email': row[4]})
            return jsonify(result)
        else:
            return jsonify({'err': 'There are no users'}), 404

    @staticmethod
    def get_by_username(username):
        cur = mysql.connection.cursor()
        sql = '''SELECT * FROM users WHERE username = %s'''
        cur.execute(sql, (username,))
        row = cur.fetchone()
        cur.close()
        if row is not None:
            return jsonify({'username': row[1], 'admin': row[3], 'email': row[4]})
        else:
            return jsonify({'Error': 'No user with that id'}), 404

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor()
        sql = '''SELECT * FROM users WHERE email = %s'''
        cur.execute(sql, (email,))
        row = cur.fetchone()
        cur.close()
        if row is not None:
            return jsonify({'username': row[1], 'admin': row[3], 'email': row[4]})
        else:
            return jsonify({'Error': 'No user with that id'}), 404

    @jwt_required
    def post(self):
        # only admin should be able to create new users
        if session.get('admin') == 0:
            response = jsonify({'err': 'Only admin can create new users'})
            response.code = 403
            return response

        args = parser.parse_args()
        if 'username' in args and 'password' in args and 'email' in args:
            admin = 0
            if 'admin' in args:
                admin = args['admin']
            cur = mysql.connection.cursor()
            sql = '''INSERT INTO users (username, password, admin, email) VALUES (%s, %s, %s, %s)'''
            cur.execute(sql, (args['username'], generate_password_hash(args['password']), admin, args['email'],))
            mysql.connection.commit()
            cur.close()
            response = jsonify({'msg': 'User inserted'})
            response.status_code = 201
            return response
        else:
            response = jsonify({'err': "Not enough parameters to create a user"})
            response.status_code = 400
            return response

@jwt.expired_token_loader
def my_expired_token_callback():
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The token has expired'
    }), 401

@app.route('/login', methods=['POST'])
def login():
    current_user = get_jwt_identity()
    print(current_user)

    args = parser.parse_args()

    if 'username' not in args or 'password' not in args:
        return jsonify({"err": "You must provide user and password parameters"}), 400
    username = args['username']
    password = args['password']
    print(generate_password_hash(password))
    cur = mysql.connection.cursor()
    sql = '''SELECT id, password, admin FROM users WHERE username = %s'''
    cur.execute(sql, (username,))
    row = cur.fetchone()
    mysql.connection.commit()
    cur.close()

    if row:
        if check_password_hash(row[1], password):
            session['user_id'] = row[0]
            session['admin'] = row[2]
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        return jsonify({"err": "Wrong password."}), 401
    else:
        return jsonify({"err": "No user with that username"}), 404


@app.route('/')
def hello_world():
    return 'Hello, use API please!'


api.add_resource(Users, '/users')
api.add_resource(User, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run()
