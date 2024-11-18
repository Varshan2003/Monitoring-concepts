from flask import Flask, jsonify, Response
import random
import time
import logging
import psutil
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of requests')
SUCCESS_COUNT = Counter('flask_app_success_total', 'Total number of successful requests')
ERROR_COUNT = Counter('flask_app_errors_total', 'Total number of errors')
REQUEST_LATENCY = Gauge('flask_app_request_latency_seconds', 'Latency of requests')

# System metrics
CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')

# Update system metrics
def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=1))  # 1-second interval for CPU usage
    MEMORY_USAGE.set(psutil.virtual_memory().percent)  # Memory usage as a percentage

# Simple route
@app.route('/simple', methods=['GET'])
def simple_route():
    REQUEST_COUNT.inc()  # Increment the request counter
    SUCCESS_COUNT.inc()  # Increment the success counter
    return jsonify({"message": "This is a simple route!"})

# Complex route with potential for error and additional complexity
@app.route('/complex', methods=['GET'])
def complex_route():
    REQUEST_COUNT.inc()  # Increment the request counter
    start_time = time.time()
    
    try:
        logger.debug("Starting complex route processing.")
        
        # Simulate delay
        delay = random.uniform(1, 5)  # Delay between 1 to 5 seconds
        logger.debug(f"Simulating delay of {delay:.2f} seconds.")
        time.sleep(delay)
        
        # Simulate some complex logic that might throw an error
        if random.choice([True, False]):
            logger.error("Random error triggered.")
            ERROR_COUNT.inc()  # Increment the error counter
            raise ValueError("An error occurred during complex processing.")
        
        # Simulate more complex processing
        result = perform_complex_calculation()
        
        logger.debug(f"Complex calculation result: {result}")
        SUCCESS_COUNT.inc()  # Increment the success counter
        return jsonify({"message": "Complex route succeeded!", "result": result})
    
    except ValueError as e:
        logger.error(f"ValueError encountered: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error encountered: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        # Record the latency
        latency = time.time() - start_time
        REQUEST_LATENCY.set(latency)

def perform_complex_calculation():
    """
    Simulates a complex calculation with possible failure.
    """
    # Simulate some calculations that might also fail
    if random.choice([True, False]):
        logger.debug("Performing complex calculation.")
        time.sleep(random.uniform(0.5, 2))  # Simulate time-consuming computation
        return random.randint(1, 100)
    else:
        logger.debug("Complex calculation failed.")
        raise RuntimeError("Failed during complex calculation.")

# Expose metrics endpoint
@app.route('/metrics')
def metrics_endpoint():
    update_system_metrics()  # Update system metrics before exposing them
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(debug=True,port=9090)
