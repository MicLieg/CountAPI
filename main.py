import datetime
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB')]
counters = db[os.getenv('MONGO_COLLECTION')]

# Create index on counter_id
counters.create_index('counter_id', unique=True)

@app.route('/v1/count', methods=['GET'])
def increment_counter():
    counter_id = request.args.get('counter')
    user_agent = request.headers.get('User-Agent')
    ip_address = request.remote_addr
    
    # Verify counter_id is provided
    if not counter_id:
        return jsonify({'error': 'Missing counter parameter'}), 400
    # Verify counter_id contains only allowed characters (alphanumeric and hyphens)
    if not all(c.isalnum() or c == '-' for c in counter_id):
        return jsonify({'error': 'Counter ID must contain only letters, numbers, and hyphens'}), 400
    # Verify counter_id does not start/end with a hyphen or contain consecutive hyphens
    if counter_id.startswith('-') or counter_id.endswith('-') or '--' in counter_id:
        return jsonify({'error': 'Counter ID cannot start/end with a hyphen or contain consecutive hyphens'}), 400
    
    # Get current counter state before update
    current_counter = counters.find_one({'counter_id': counter_id})
    if current_counter:
        last_access = current_counter['last_access']
    else:
        last_access = None
    
    # Get current time
    now = datetime.datetime.now() # Unix timestamp as integer, more precise and standard

    # Check if the counter document exists, and initialize it if not
    if not current_counter:
        counters.insert_one({
            'counter_id': counter_id,
            'count': 0,
            'ip_list': {},
            'user_agents': [],
            'created_at': now,
            'last_access': now
        })
    
    # Aggregation pipeline to update the counter document
    pipeline = [
        {'$match': {'counter_id': counter_id}},
        {'$set': {
            'count': {'$add': ['$count', 1]},
            'last_access': now,
            'user_agents': {'$setUnion': ['$user_agents', [user_agent]]},
            'ip_list': {
                '$mergeObjects': [
                    '$ip_list',
                    {'$arrayToObject': [[{'k': ip_address, 'v': {'$add': [{'$ifNull': [{'$getField': {'field': ip_address, 'input': '$ip_list'}}, 0]}, 1]}}]]}
                ]
            }
        }},
        {'$merge': {
            'into': 'counters',
            'whenMatched': 'replace',
            'whenNotMatched': 'insert'
        }}
    ]
    
    # Run aggregation
    result = list(counters.aggregate(pipeline))
    
    # Retrieve updated counter state
    updated_counter = counters.find_one({'counter_id': counter_id})
    
    return jsonify({
        'count': updated_counter['count'],
        'last_access': last_access,
        'created_at': updated_counter['created_at'],
    })

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('FLASK_PORT'))
