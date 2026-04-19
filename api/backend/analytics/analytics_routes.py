from flask import Blueprint, jsonify
from backend.db_connection import get_db
from mysql.connector import Error

analytics = Blueprint("analytics", __name__)


@analytics.route("/dashboard/analytics", methods=["GET"])
def get_dashboard_overview():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM husky_user) AS total_users,
                (SELECT COUNT(*) FROM husky_user WHERE verification_status = 'verified') AS verified_users,
                (SELECT COUNT(*) FROM husky_match) AS total_matches,
                (SELECT COUNT(*) FROM husky_match WHERE status = 'active') AS active_matches
        """)
        return jsonify(cursor.fetchone()), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/dashboard/analytics/satisfaction", methods=["GET"])
def get_satisfaction_stats():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                ROUND(AVG(rating), 2) AS avg_satisfaction,
                COUNT(*) AS total_responses,
                MIN(rating) AS lowest_rating,
                MAX(rating) AS highest_rating
            FROM match_feedback
        """)
        return jsonify(cursor.fetchone()), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/dashboard/analytics/demographics", methods=["GET"])
def get_demographics():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT year, COUNT(*) AS user_count
            FROM husky_user
            GROUP BY year
            ORDER BY user_count DESC
        """)
        by_year = cursor.fetchall()

        cursor.execute("""
            SELECT m.major_name, COUNT(*) AS user_count
            FROM student_major_tags smt
            JOIN majors m ON smt.major_id = m.major_id
            GROUP BY m.major_name
            ORDER BY user_count DESC
            LIMIT 10
        """)
        by_major = cursor.fetchall()

        cursor.execute("""
            SELECT it.tag_type, COUNT(*) AS user_count
            FROM student_interest si
            JOIN interest_tag it ON si.interest_id = it.tag_id
            GROUP BY it.tag_type
            ORDER BY user_count DESC
        """)
        by_interest = cursor.fetchall()

        return jsonify({
            "by_year": by_year,
            "by_major": by_major,
            "by_interest": by_interest
        }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/dashboard/analytics/meetups", methods=["GET"])
def get_meetup_rate():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                COUNT(DISTINCT hm.match_id) AS total_matches,
                COUNT(DISTINCT mp.match_id) AS matches_with_photo,
                ROUND(
                    COUNT(DISTINCT mp.match_id) * 100.0 /
                    NULLIF(COUNT(DISTINCT hm.match_id), 0), 2
                ) AS meetup_rate_percent
            FROM husky_match hm
            LEFT JOIN meetup_photo mp ON mp.match_id = hm.match_id
        """)
        return jsonify(cursor.fetchone()), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/dashboard/analytics/trends", methods=["GET"])
def get_trends():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                YEAR(matched_on) AS year,
                MONTH(matched_on) AS month,
                COUNT(*) AS new_matches
            FROM husky_match
            GROUP BY YEAR(matched_on), MONTH(matched_on)
            ORDER BY year ASC, month ASC
        """)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@analytics.route("/dashboard/analytics/match-success", methods=["GET"])
def get_match_success():
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                m1.major_name AS student1_major,
                m2.major_name AS student2_major,
                COUNT(*) AS total_matches,
                ROUND(AVG(mf.rating), 2) AS avg_satisfaction
            FROM husky_match hm
            JOIN student_major_tags sm1 ON hm.student1_id = sm1.student_id
            JOIN student_major_tags sm2 ON hm.student2_id = sm2.student_id
            JOIN majors m1 ON sm1.major_id = m1.major_id
            JOIN majors m2 ON sm2.major_id = m2.major_id
            LEFT JOIN match_feedback mf ON hm.match_id = mf.match_id
            GROUP BY m1.major_name, m2.major_name
            ORDER BY avg_satisfaction DESC
        """)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()