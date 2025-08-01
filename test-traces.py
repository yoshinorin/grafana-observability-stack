#!/usr/bin/env python3
"""
Sample trace generator for testing the observability stack
"""


import time
import random
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def setup_tracing():
    """Set up OpenTelemetry tracing"""
    resource = Resource.create({
        "service.name": "sample-app",
        "service.version": "1.0.0",
        "deployment.environment": "test"
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Configure OTLP exporter
    # Use environment variable for endpoint (Docker-friendly)
    import os
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    otlp_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    return trace.get_tracer("sample-app", "1.0.0")

def simulate_user_request(tracer):
    """Simulate a user request with multiple spans"""
    with tracer.start_as_current_span("user_request") as parent_span:
        parent_span.set_attribute("http.method", "GET")
        parent_span.set_attribute("http.url", "/api/users/123")
        parent_span.set_attribute("http.status_code", 200)
        parent_span.set_attribute("user.id", "123")

        print("[user_request] User request started user.id=123")
        logging.info("[user_request] User request started user.id=123")

        # Simulate authentication
        with tracer.start_as_current_span("authenticate_user") as auth_span:
            logging.info("[authenticate_user] Authentication started user.id=123")
            auth_span.set_attribute("auth.method", "jwt")
            time.sleep(random.uniform(0.01, 0.05))  # 10-50ms
            auth_span.set_attribute("auth.success", True)
            logging.info("[authenticate_user] Authentication succeeded user.id=123")

        # Simulate database query
        with tracer.start_as_current_span("database_query") as db_span:
            logging.info("[database_query] DB query started table=users")
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "users")
            time.sleep(random.uniform(0.02, 0.1))  # 20-100ms
            db_span.set_attribute("db.rows_affected", 1)
            logging.info("[database_query] DB query finished table=users rows=1")

        # Simulate external API call
        with tracer.start_as_current_span("external_api_call") as api_span:
            logging.info("[external_api_call] External API call started")
            api_span.set_attribute("http.method", "GET")
            api_span.set_attribute("http.url", "https://external.example.com/profile")
            time.sleep(random.uniform(0.05, 0.2))  # 50-200ms

            # Sometimes simulate an error
            if random.random() < 0.1:  # 10% error rate
                api_span.set_attribute("error", True)
                api_span.set_attribute("http.status_code", 500)
                parent_span.set_attribute("http.status_code", 500)
                print("[external_api_call] External API error status=500")
                logging.error("[external_api_call] External API error status=500")
            else:
                api_span.set_attribute("http.status_code", 200)
                logging.info("[external_api_call] External API call succeeded status=200")

        # Simulate response processing
        with tracer.start_as_current_span("process_response") as process_span:
            process_span.set_attribute("response.size", random.randint(500, 2000))
            time.sleep(random.uniform(0.005, 0.02))  # 5-20ms
            logging.info("[process_response] Response processing finished")

def simulate_order_process(tracer):
    """Simulate a more complex order processing workflow"""
    with tracer.start_as_current_span("order_process") as order_span:
        order_id = random.randint(1000, 9999)
        order_span.set_attribute("order.id", order_id)
        order_span.set_attribute("http.method", "POST")
        order_span.set_attribute("http.url", "/api/orders")

        print(f"[order_process] Order process started order.id={order_id}")
        logging.info(f"[order_process] Order process started order.id={order_id}")

        # Validate order
        with tracer.start_as_current_span("validate_order") as validate_span:
            items_count = random.randint(1, 5)
            validate_span.set_attribute("order.items_count", items_count)
            logging.info(f"[validate_order] Order validation items_count={items_count}")
            time.sleep(random.uniform(0.01, 0.03))

        # Check inventory
        with tracer.start_as_current_span("check_inventory") as inventory_span:
            inventory_span.set_attribute("inventory.check_type", "real_time")
            logging.info("[check_inventory] Inventory check started")
            time.sleep(random.uniform(0.03, 0.08))
            inventory_span.set_attribute("inventory.available", True)
            logging.info("[check_inventory] Inventory available")

        # Process payment
        with tracer.start_as_current_span("process_payment") as payment_span:
            payment_span.set_attribute("payment.method", "credit_card")
            amount = random.uniform(10.0, 500.0)
            payment_span.set_attribute("payment.amount", amount)
            logging.info(f"[process_payment] Payment process started amount={amount:.2f}")
            time.sleep(random.uniform(0.1, 0.3))  # Payment takes longer

            # Sometimes payment fails
            if random.random() < 0.05:  # 5% failure rate
                payment_span.set_attribute("payment.status", "failed")
                payment_span.set_attribute("error", True)
                order_span.set_attribute("http.status_code", 402)
                print(f"[process_payment] Payment failed order.id={order_id}")
                logging.error(f"[process_payment] Payment failed order.id={order_id}")
                return
            else:
                payment_span.set_attribute("payment.status", "success")
                logging.info(f"[process_payment] Payment succeeded order.id={order_id}")

        # Update database
        with tracer.start_as_current_span("update_order_database") as update_span:
            update_span.set_attribute("db.system", "postgresql")
            update_span.set_attribute("db.operation", "INSERT")
            update_span.set_attribute("db.table", "orders")
            logging.info("[update_order_database] Order database updated")
            time.sleep(random.uniform(0.02, 0.06))

        # Send notification
        with tracer.start_as_current_span("send_notification") as notify_span:
            notify_span.set_attribute("notification.type", "email")
            notify_span.set_attribute("notification.recipient", "user@example.com")
            logging.info("[send_notification] Notification sent user@example.com")
            time.sleep(random.uniform(0.01, 0.04))

        order_span.set_attribute("http.status_code", 201)
        order_span.set_attribute("order.status", "completed")
        logging.info(f"[order_process] Order process finished order.id={order_id}")

def main():
    print("🚀 Starting trace generation...")
    print("📊 Sending traces to http://localhost:4317")
    print("🔍 View traces in Grafana: http://localhost:3001")
    print("⏱️  Generating traces for 30 seconds...")
    
    tracer = setup_tracing()
    
    start_time = time.time()
    trace_count = 0
    
    # Generate traces for 30 seconds
    while time.time() - start_time < 30:  # 30 seconds
        # Mix different types of requests
        if random.random() < 0.7:  # 70% user requests
            simulate_user_request(tracer)
        else:  # 30% order processes
            simulate_order_process(tracer)
        
        trace_count += 1
        
        # Wait between requests (simulate realistic traffic)
        time.sleep(random.uniform(0.1, 0.5))  # Shorter wait for quicker testing
        
        if trace_count % 5 == 0:
            print(f"📈 Generated {trace_count} traces...")
    
    print(f"✅ Completed! Generated {trace_count} sample traces")
    print("📋 Next steps:")
    print("   1. Open Grafana: http://localhost:3001")
    print("   2. Go to Explore → Tempo")
    print("   3. Search for traces with service.name='sample-app'")

if __name__ == "__main__":
    main()
