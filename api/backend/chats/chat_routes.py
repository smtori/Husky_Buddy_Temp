from flask import Blueprint, jsonify, request
from backend.db_connection import get_db

chat = Blueprint('chat', __name__)

# Get all messages for a match
@chat.route('/chat/<int:match_id>', methods=['GET'])
def get_messages(match_id):
    cursor = get_db().cursor()
    query = """
        SELECT cm.message_id, cm.sender_id, cm.content, cm.sent_at,
               hu.first_name, hu.last_name
        FROM chat_message cm
        JOIN husky_user hu ON cm.sender_id = hu.student_id
        WHERE cm.match_id = %s
        ORDER BY cm.sent_at ASC
    """
    cursor.execute(query, (match_id,))
    rows = cursor.fetchall()

    messages = []
    for row in rows:
        messages.append({
            "message_id": row[0],
            "sender_id": row[1],
            "content": row[2],
            "sent_at": str(row[3]),
            "sender_name": f"{row[4]} {row[5]}"
        })

    return jsonify(messages)

# Send a message
@chat.route('/chat/<int:match_id>', methods=['POST'])
def send_message(match_id):
    data = request.get_json()

    cursor = get_db().cursor()

    # Verify the sender is part of this match
    cursor.execute("""
        SELECT match_id FROM husky_match
        WHERE match_id = %s AND (student1_id = %s OR student2_id = %s)
    """, (match_id, data['sender_id'], data['sender_id']))

    if cursor.fetchone() is None:
        return jsonify({"error": "You are not part of this match"}), 403

    cursor.execute("""
        INSERT INTO chat_message (match_id, sender_id, content)
        VALUES (%s, %s, %s)
    """, (match_id, data['sender_id'], data['content']))
    get_db().commit()

    return jsonify({"message": "Message sent"}), 201

# Get a random active match for a user (for the "random chat" feature)
@chat.route('/chat/random/<int:user_id>', methods=['GET'])
def random_match(user_id):
    cursor = get_db().cursor()
    query = """
        SELECT hm.match_id, hm.student1_id, hm.student2_id,
               u1.first_name AS u1_first, u1.last_name AS u1_last,
               u2.first_name AS u2_first, u2.last_name AS u2_last
        FROM husky_match hm
        JOIN husky_user u1 ON hm.student1_id = u1.student_id
        JOIN husky_user u2 ON hm.student2_id = u2.student_id
        WHERE hm.status = 'active'
          AND (hm.student1_id = %s OR hm.student2_id = %s)
        ORDER BY RAND()
        LIMIT 1
    """
    cursor.execute(query, (user_id, user_id))
    row = cursor.fetchone()

    if row is None:
        return jsonify({"error": "No active matches found"}), 404

    # Figure out who the buddy is
    if row[1] == user_id:
        buddy_name = f"{row[5]} {row[6]}"
    else:
        buddy_name = f"{row[3]} {row[4]}"

    return jsonify({
        "match_id": row[0],
        "buddy_name": buddy_name
    })