
import csv
import math

requests = []

with open("inference_metrics.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        duration_ns = int(row["total_duration_ns"])
        duration_seconds = duration_ns / 1_000_000_000

        load_ns = int(row["load_duration_ns"])
        load_seconds = load_ns / 1_000_000_000

        requests.append({
            "total_seconds": duration_seconds,
            "load_seconds": load_seconds
        })
cold_starts = []
warm_requests = []

for request in requests:
    if request["load_seconds"] > 0.1:
        cold_starts.append(request)
    else:
        warm_requests.append(request)
        

print(f"Cold starts: {len(cold_starts)}")
print(f"Warm requests: {len(warm_requests)}")

# Extract measurements from the request records
total_durations = [request["total_seconds"] for request in requests]
load_durations = [request["load_seconds"] for request in requests]

total_durations.sort()

average_load = sum(load_durations) / len(load_durations)
maximum_load = max(load_durations)

p95_index = math.ceil(0.95 * len(total_durations)) - 1
p95_latency = total_durations[p95_index]

average = sum(total_durations) / len(total_durations)
fastest = min(total_durations)
slowest = max(total_durations)

print(f"Requests analyzed: {len(requests)}")
print(f"Average model load time: {average_load:.4f} seconds")
print(f"Maximum model load time: {maximum_load:.4f} seconds")
print(f"P95 latency: {p95_latency:.2f} seconds")
print(f"Average latency: {average:.2f} seconds")
print(f"Fastest request: {fastest:.2f} seconds")
print(f"Slowest request: {slowest:.2f} seconds")
