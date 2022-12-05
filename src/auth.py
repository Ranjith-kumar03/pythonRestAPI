from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, \
    HTTP_401_UNAUTHORIZED, HTTP_200_OK
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, get_jwt_identity

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(password) < 6:
        return jsonify({"error": "Password Too Short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({"error": "Username Too Short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum or " " in username:
        return jsonify({"error": "Username should be alphanumberic and no space should be there"}), HTTP_400_BAD_REQUEST
    if not validators.email(email):
        return jsonify({"error": "Email not in Email format"}), HTTP_400_BAD_REQUEST
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email already exists"}), HTTP_409_CONFLICT
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "username already exists"}), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)
    user = User(
        username=username,
        password=password_hash,
        email=email,

    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": f'{user.username} created',
                    "user": {
                        "username": username,
                        "email": email
                    }
                    }
                   ), HTTP_201_CREATED


@auth.post("/login")
def login():
    email = request.json.get("email", '')
    password = request.json.get("password", '')
    _user = User.query.filter_by(email=email).first()
    print("see the user logged in", _user)
    if _user is None:
        return jsonify({"error": "username doesnot  exists"}), HTTP_409_CONFLICT
    if _user:
        password_correct = check_password_hash(_user.password, password)
        if password_correct:
            access = create_access_token(identity=_user.id)
            refresh = create_refresh_token(identity=_user.id)
            print("see access token",access,refresh)
            return jsonify({
                "user": {
                    "username": _user.username,
                    "email":_user.email,
                    "accesstoken": access,
                    "refreshtoken": refresh
                }
            }),HTTP_200_OK
            # return jsonify({
            #     "user": {
            #         "user": _user,
            #         "accesstoken": access,
            #         "refreshtoken": refresh
            #     }
            # })
        else:
            return jsonify({"password_error": "password doesnot  match"}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def getme1():
    # import pdb
    # pdb.set_trace()
    user_id = get_jwt_identity()
    user_found = User.query.filter_by(id=user_id).first()
    return jsonify({
        "user":{
            "username": user_found.username,
            "email":user_found.email
        }
    }),HTTP_200_OK

@auth.post("/token/refresh")
@auth.get("/token/refresh")
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    acessToken = create_access_token(identity=identity)
    return jsonify({
        "user": {
           "accesstoken": acessToken,
            }
    }), HTTP_200_OK

