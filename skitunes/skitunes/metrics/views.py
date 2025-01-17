from skitunes import app
from flask import jsonify

@app.route('/health')
def health_check():
    """
    Health check endpoint to verify application is running correctly.
    
    Returns:
    - 200 OK if the application is ready to receive traffic
    - Optionally, you can add more sophisticated checks here
    """
    try:
        # Add any critical dependency checks here
        # For example, check database connection, external service availability, etc.
        
        # Basic health check
        return jsonify({
            "status": "healthy",
            "message": "Application is running correctly"
        }), 200
    except Exception as e:
        # Log the error (use your preferred logging method)
        return jsonify({
            "status": "unhealthy",
            "message": str(e)
        }), 500