from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import *
from src.database import Bookmark, db
import validators
from flask_jwt_extended import get_jwt_identity, get_current_user, jwt_required

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    currentuser = get_jwt_identity()
    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                "error": "Enter A valid URL"
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "error": "URL Already Exists"
            }), HTTP_409_CONFLICT
        bookmark = Bookmark(
            body=body,
            url=url,
            user_id=currentuser

        )
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "bookmark": {
                "id": bookmark.id,
                "url": bookmark.url,
                "body": bookmark.body,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at
            }
        }), HTTP_201_CREATED
    else:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)
        bookmarks = Bookmark.query.filter_by(user_id=currentuser).paginate(page=page, per_page=per_page)
        data = []
        for bookmark in bookmarks.items:
            data.append({
                "id": bookmark.id,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "body": bookmark.body,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at
            })
        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "prev_page": bookmarks.prev_num,
            "next_page": bookmarks.next_num,
            "has_next": bookmarks.has_next,
            "has_prev": bookmarks.has_prev
        }

        return jsonify({
            "data": data, "meta": meta
        }), HTTP_200_OK


@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    print("Iam hit by browser")
    currentuser = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=currentuser, id=id).first()
    if bookmark:
        return jsonify({
            "bookmark": {
                "id": bookmark.id,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "body": bookmark.body,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at
            }
        }), HTTP_200_OK
    else:
        return jsonify({
            "message": "no items found"
        }), HTTP_404_NOT_FOUND


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def editbookmark(id):
    currentuser = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=currentuser, id=id).first()
    if not bookmark:
        return jsonify({
            "message": "no items found"
        }), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')
    if not validators.url(url):
        return jsonify({
            "error": "Enter A valid URL"
        }), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter_by(url=url).first():
        return jsonify({
            "error": "URL Already Exists"
        }), HTTP_409_CONFLICT
    bookmark.body = body
    bookmark.url = url
    db.session.commit()
    return jsonify({
        "bookmark": {
            "id": bookmark.id,
            "url": bookmark.url,
            "body": bookmark.body,
            "short_url": bookmark.short_url,
            "visits": bookmark.visits,
            "created_at": bookmark.created_at,
            "updated_at": bookmark.updated_at
        }
    }), HTTP_201_CREATED


@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    print("Iam hit by browser")
    currentuser = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=currentuser, id=id).first()
    if not bookmark:
        return jsonify({
            "message": "no items found"
        }), HTTP_404_NOT_FOUND
    db.session.delete(bookmark)
    db.session.commit()
    return  jsonify({}),HTTP_204_NO_CONTENT

@bookmarks.get("/stats")
@jwt_required()
def get_stats():
    currentuser = get_jwt_identity()
    data=[]
    items = Bookmark.query.filter_by(user_id=currentuser).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url
        }
        data.append(new_link)

    return jsonify({'data':data}),HTTP_200_OK
