from flask import Blueprint, jsonify, request
from backend.db_connection import get_db

users = Blueprint('users', __name__)

@users.route('/users', methods=['GET'])
def get_users():
    cursor = get_db().cursor()

    query = """
        SELECT student_id, first_name, last_name, email, year, verification_status
        FROM husky_user
        ORDER BY student_id
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    result = []
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
def get_user(user_id):
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

@users.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    query = """
        INSERT INTO husky_user (student_id, first_name, last_name, email, year, verification_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor = get_db().cursor()
    cursor.execute(query, (
        data['student_id'],
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