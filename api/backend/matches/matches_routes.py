from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

matches = Blueprint("matches", __name__)


@matches.route("/matches", methods=["GET"])
def get_all_matches():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /matches")

        status = request.args.get("status")
        student_id = request.args.get("student_id")

        query = "SELECT * FROM husky_match WHERE 1=1"
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        if student_id:
            query += " AND (student1_id = %s OR student2_id = %s)"
            params.extend([student_id, student_id])

        cursor.execute(query, params)
        match_list = cursor.fetchall()

        return jsonify(match_list), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_matches: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@matches.route("/matches/<int:match_id>", methods=["GET"])
def get_match(match_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT 
                hm.match_id,
                hm.status,
                hm.matched_on,
                u1.student_id AS student1_id,
                u1.first_name AS student1_first_name,
                u1.last_name AS student1_last_name,
                u1.email AS student1_email,
                u2.student_id AS student2_id,
                u2.first_name AS student2_first_name,
                u2.last_name AS student2_last_name,
                u2.email AS student2_email
            FROM husky_match hm
            JOIN husky_user u1 ON hm.student1_id = u1.student_id
            JOIN husky_user u2 ON hm.student2_id = u2.student_id
            WHERE hm.match_id = %s
        """
        cursor.execute(query, (match_id,))
        match = cursor.fetchone()

        if not match:
            return jsonify({"error": "Match not found"}), 404

        return jsonify(match), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@matches.route("/users/<int:student_id>/matches/previous", methods=["GET"])
def get_previous_matches(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        # Get all previous matches (not active) for the user
        query = """
            SELECT 
                hm.match_id,
                hm.status,
                hm.matched_on,
                CASE 
                    WHEN hm.student1_id = %s THEN hm.student2_id
                    ELSE hm.student1_id
                END AS buddy_id,
                CASE 
                    WHEN hm.student1_id = %s THEN CONCAT(u2.first_name, ' ', u2.last_name)
                    ELSE CONCAT(u1.first_name, ' ', u1.last_name)
                END AS buddy_name,
                MAX(m.meetup_date) AS last_activity
            FROM husky_match hm
            LEFT JOIN husky_user u1 ON hm.student1_id = u1.student_id
            LEFT JOIN husky_user u2 ON hm.student2_id = u2.student_id
            LEFT JOIN meetup m ON hm.match_id = m.match_id
            WHERE (hm.student1_id = %s OR hm.student2_id = %s)
            GROUP BY hm.match_id, hm.status, hm.matched_on, buddy_id, buddy_name
            ORDER BY hm.matched_on DESC
        """
        cursor.execute(query, (student_id, student_id, student_id, student_id))
        matches = cursor.fetchall()

        # For each match, get feedback ratings
        for match in matches:
            feedback_query = """
                SELECT rating, comment
                FROM match_feedback
                WHERE match_id = %s AND student_id = %s
            """
            cursor.execute(feedback_query, (match['match_id'], student_id))
            feedback = cursor.fetchone()
            
            if feedback:
                match['your_rating'] = feedback['rating']
                match['your_comment'] = feedback['comment']
            else:
                match['your_rating'] = 0
                match['your_comment'] = None

        return jsonify(matches), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_previous_matches: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@matches.route("/matches", methods=["POST"])
def create_match():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ["student1_id", "student2_id", "status", "matched_on"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        if data["student1_id"] == data["student2_id"]:
            return jsonify({"error": "A user cannot be matched with themselves"}), 400

        cursor.execute("SELECT student_id FROM husky_user WHERE student_id = %s", (data["student1_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "student1_id not found"}), 404

        cursor.execute("SELECT student_id FROM husky_user WHERE student_id = %s", (data["student2_id"],))
        if not cursor.fetchone():
            return jsonify({"error": "student2_id not found"}), 404

        query = """
            INSERT INTO husky_match (student1_id, student2_id, status, matched_on)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["student1_id"],
            data["student2_id"],
            data["status"],
            data["matched_on"]
        ))

        get_db().commit()
        return jsonify({
            "message": "Match created successfully",
            "match_id": cursor.lastrowid
        }), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@matches.route("/matches/<int:match_id>", methods=["PUT"])
def update_match(match_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        cursor.execute("SELECT match_id FROM husky_match WHERE match_id = %s", (match_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Match not found"}), 404

        allowed_fields = ["status", "matched_on"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(match_id)
        query = f"UPDATE husky_match SET {', '.join(update_fields)} WHERE match_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Match updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@matches.route("/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT match_id FROM husky_match WHERE match_id = %s", (match_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Match not found"}), 404

        cursor.execute("DELETE FROM husky_match WHERE match_id = %s", (match_id,))
        get_db().commit()

        return jsonify({"message": "Match deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Get all meetup photos for a user
@matches.route("/users/<int:student_id>/photos", methods=["GET"])
def get_user_photos(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
    SELECT mp.photo_id, mp.photo_url, mp.caption, mp.uploaded_at, u.first_name, u.last_name
    FROM meetup_photo mp
    JOIN husky_user u ON mp.uploaded_by = u.student_id
    WHERE mp.match_id IN (
        SELECT match_id FROM husky_match 
        WHERE student1_id = %s OR student2_id = %s
    )
    ORDER BY mp.uploaded_at DESC
""", (student_id, student_id))
        photos = cursor.fetchall()
        return jsonify(photos), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Upload a new meetup photo
@matches.route("/users/<int:student_id>/photos", methods=["POST"])
def upload_photo(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ["match_id", "photo_url"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        cursor.execute("""
            INSERT INTO meetup_photo (match_id, uploaded_by, photo_url, caption)
            VALUES (%s, %s, %s, %s)
        """, (
            data["match_id"],
            student_id,
            data["photo_url"],
            data.get("caption", "")
        ))
        get_db().commit()
        return jsonify({
            "message": "Photo uploaded successfully",
            "photo_id": cursor.lastrowid
        }), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()