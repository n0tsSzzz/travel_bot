from prometheus_client import CollectorRegistry, Counter

# registry = CollectorRegistry()


RABBITMQ_MESSAGES_PRODUCED = Counter("consumer_rabbitmq_messages_produced_total", "Total messages produced to RabbitMQ")
RABBITMQ_MESSAGES_CONSUMED = Counter(
    "consumer_rabbitmq_messages_consumed_totals", "Total messages consumed from RabbitMQ"
)
REQUESTS_TOTAL = Counter("consumer_http_requests_total", "Total HTTP Requests", ["status_code", "path"])
