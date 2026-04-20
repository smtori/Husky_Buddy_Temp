from flask import Blueprint, jsonify, request, Response
from backend.db_connection import get_db
from typing import List, Dict, Any

users = Blueprint('users', __name__)

@users.route('/users', methods=['GET'])
def get_users() -> Response:

    cursor = get_db().cursor()

    query = """
        SELECT student_id, first_name, last_name, email, year, verification_status
        FROM husky_user
        ORDER BY student_id
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # creating a list of dicts that will be converted to json
    result: List[Dict[str, Any]] = []

    # appending each sql row to list, each row is represented as a dict.
    for row in rows:
        result.append({
            "student_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "name": f"{row[1]} {row[2]}",
            "email": row[3],
            "year": row[4],
            "status": row[5]
        })

    return jsonify(result)


@users.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id) -> Response:
    cursor = get_db().cursor()

    query = """
        SELECT student_id, first_name, last_name, email, year, verification_status
        FROM husky_user
        WHERE student_id = %s
    """

    cursor.execute(query, (user_id,))
    row = cursor.fetchone()

    if row is None:
        return jsonify({"error": "User not found"}), 404

    result = {
        "student_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "name": f"{row[1]} {row[2]}",
        "email": row[3],
        "year": row[4],
        "status": row[5]
    }

    return jsonify(result)


@users.route('/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id) -> Response:
    cursor = get_db().cursor()

    # Basic user info
    cursor.execute("""
        SELECT student_id, first_name, last_name, email, year, verification_status
        FROM husky_user
        WHERE student_id = %s
    """, (user_id,))
    user_row = cursor.fetchone()

    if user_row is None:
        return jsonify({"error": "User not found"}), 404

    # Majors (via student_major_tags -> majors)
    cursor.execute("""
        SELECT m.major_name
        FROM student_major_tags smt
        JOIN majors m ON smt.major_id = m.major_id
        WHERE smt.student_id = %s
        ORDER BY m.major_name
    """, (user_id,))
    majors = [r[0] for r in cursor.fetchall()]

    # Interests (via student_interest -> interest_tag)
    cursor.execute("""
        SELECT it.tag_type
        FROM student_interest si
        JOIN interest_tag it ON si.interest_id = it.tag_id
        WHERE si.student_id = %s
        ORDER BY it.tag_type
    """, (user_id,))
    interests = [r[0] for r in cursor.fetchall()]

    # Favorite campus spots (via student_spots -> campus_spot)
    cursor.execute("""
        SELECT cs.spot_name, cs.location
        FROM student_spots ss
        JOIN campus_spot cs ON ss.spot_id = cs.spot_id
        WHERE ss.student_id = %s
        ORDER BY cs.spot_name
    """, (user_id,))
    spots = [{"spot_name": r[0], "location": r[1]} for r in cursor.fetchall()]

    result = {
        "student_id": user_row[0],
        "first_name": user_row[1],
        "last_name": user_row[2],
        "name": f"{user_row[1]} {user_row[2]}",
        "email": user_row[3],
        "year": user_row[4],
        "status": user_row[5],
        "majors": majors,
        "interests": interests,
        "campus_spots": spots,
    }

    return jsonify(result)


@users.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    query = """
        INSERT INTO husky_user (first_name, last_name, email, year, verification_status)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor = get_db().cursor()
    cursor.execute(query, (
        data['first_name'],
        data['last_name'],
        data['email'],
        data['year'],
        data['status']
    ))
    get_db().commit()

    return jsonify({"message": "User created successfully"}), 201


@users.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    query = """
        UPDATE husky_user
        SET first_name = %s,
            last_name = %s,
            email = %s,
            year = %s,
            verification_status = %s
        WHERE student_id = %s
    """

    cursor = get_db().cursor()
    cursor.execute(query, (
        data['first_name'],
        data['last_name'],
        data['email'],
        data['year'],
        data['status'],
        user_id
    ))
    get_db().commit()

    return jsonify({"message": f"User {user_id} updated successfully"})


@users.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    query = """
        DELETE FROM husky_user
        WHERE student_id = %s
    """

    cursor = get_db().cursor()
    cursor.execute(query, (user_id,))
    get_db().commit()

    return jsonify({"message": f"User {user_id} deleted successfully"})