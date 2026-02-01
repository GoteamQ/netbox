import django_rq
from netbox.config import get_config

# Get connection
redis_conn = django_rq.get_connection('default')

# Check keys for Discovery request 22 (seen in logs)
log_id = 22
total_key = f'discovery:{log_id}:batches:total'
done_key = f'discovery:{log_id}:batches:done'

total = redis_conn.get(total_key)
done = redis_conn.get(done_key)

print(f"Discovery Log {log_id} stats:")
print(f"Total Batches expected: {total}")
print(f"Batches reported done: {done}")

# basic queue len check
queue = django_rq.get_queue('default')
print(f"Remaining jobs in default queue: {queue.count}")
