from flask import Blueprint, jsonify, request, Response
from backend.db_connection import get_db
from typing import Any, List

# the name 'campus_spots' should be used for blueprint registration
campus_spots = Blueprint('campus_spots', __name__)

get_spots_query = """
    SELECT * FROM campus_spot;
"""

delete_spots_query = """
    DELETE FROM campus_spot
    WHERE spot_id = %s;
"""

update_spot_query = """
    UPDATE campus_spot
    SET spot_name = %s, location = %s
    WHERE spot_id = %s;
"""

create_spot_query = """
    INSERT INTO campus_spot (spot_name, location)
    VALUES (%s, %s);
"""

# get all campus spots
@campus_spots.route('/campus-spots', methods=['GET']) # type: ignore
def get_campus_spots() -> Response:
    """
    simple SELECT * FROM campus_spots
    returns all 

    will return 500 on db error
    """
    on_failure_return: Response = jsonify({"error": "Unknown error"}), 500

    try:
        cursor = get_db().cursor()
        cursor.execute(get_spots_query)
        rows = cursor.fetchall()

        output: List[Any] = []
        for row in rows:
            output.append({
                "spot_id": row[0],
                "spot_name": row[1],
                "location": row[2],
            })

        return jsonify(output), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # this statement should never execute - it's here for type safety
    return on_failure_return

# delete a campus spot
@campus_spots.route('/campus-spots/<int:spot_id>', methods=['DELETE']) # type: ignore
def delete_campus_spot(spot_id: int) -> Response:
    """
    Deletes a campus spot by spot_id from the database.
    Returns 404 if spot doesn't exist, 500 on database error.
    """
    try:
        cursor = get_db().cursor()
        
        # Check if spot exists
        cursor.execute("SELECT spot_id FROM campus_spot WHERE spot_id = %s", (spot_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Campus spot not found"}), 404
        
        # Delete the spot
        cursor.execute(delete_spots_query, (spot_id,))
        get_db().commit()
        
        return jsonify({"message": "Campus spot deleted successfully"}), 200
    
    # error handling below
    except Exception as e:
        get_db().rollback()
        return jsonify({"error": str(e)}), 500

# update a campus spot
@campus_spots.route('/campus-spots/<int:spot_id>', methods=['PUT']) # type: ignore
def update_campus_spot(spot_id: int) -> Response:
    """
    Updates a campus spot's name and/or location.
    Expects JSON body with 'spot_name' and/or 'location' fields.
    Returns 404 if spot not found, 400 if missing required fields, 500 on error.
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or ('spot_name' not in data and 'location' not in data):
            return jsonify({"error": "Must provide 'spot_name' and/or 'location'"}), 400
        
        cursor = get_db().cursor()
        
        # Check if spot exists
        cursor.execute("SELECT spot_id FROM campus_spot WHERE spot_id = %s", (spot_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Campus spot not found"}), 404
        
        # Get current values if not provided
        spot_name = data.get('spot_name')
        location = data.get('location')
        
        if spot_name is None or location is None:
            cursor.execute("SELECT spot_name, location FROM campus_spot WHERE spot_id = %s", (spot_id,))
            current = cursor.fetchone()
            if spot_name is None:
                spot_name = current[0]
            if location is None:
                location = current[1]
        
        # Update the spot
        cursor.execute(update_spot_query, (spot_name, location, spot_id))
        get_db().commit()
        
        return jsonify({"message": "Campus spot updated successfully"}), 200
    
    except Exception as e:
        get_db().rollback()
        return jsonify({"error": str(e)}), 500

# create a new campus spot
@campus_spots.route('/campus-spots', methods=['POST']) # type: ignore
def create_campus_spot() -> Response:
    """
    Creates a new campus spot.
    Expects JSON body with 'spot_name' and 'location' fields.
    Returns 400 if missing required fields, 201 on success, 500 on error.
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'spot_name' not in data or 'location' not in data:
            return jsonify({"error": "Must provide 'spot_name' and 'location'"}), 400
        
        # Validate fields aren't empty
        spot_name = data.get('spot_name', '').strip()
        location = data.get('location', '').strip()
        
        if not spot_name or not location:
            return jsonify({"error": "'spot_name' and 'location' cannot be empty"}), 400
        
        cursor = get_db().cursor()
        
        # Insert the new spot
        cursor.execute(create_spot_query, (spot_name, location))
        get_db().commit()
        
        # Get the newly created spot's ID
        spot_id = cursor.lastrowid
        
        return jsonify({
            "message": "Campus spot created successfully",
            "spot_id": spot_id,
            "spot_name": spot_name,
            "location": location
        }), 201
    
    except Exception as e:
        get_db().rollback()
        return jsonify({"error": str(e)}), 500



