
import csv
import math

requests = []

# Read inference metrics
with open("inference_metrics.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        requests.append({
            "total_seconds": int(row["total_duration_ns"]) / 1_000_000_000,
            "load_seconds": int(row["load_duration_ns"]) / 1_000_000_000,
            "prompt_duration_seconds": int(row["prompt_eval_duration_ns"]) / 1_000_000_000,
            "prompt_tokens": int(row["prompt_eval_count"]),
            "generation_duration_seconds": int(row["eval_duration_ns"]) / 1_000_000_000,
            "generation_tokens": int(row["eval_count"]),
            "elapsed_seconds": float(row["elapsed_seconds"]),
            "cpu_before": float(row["cpu_before_percent"]),
            "cpu_after": float(row["cpu_after_percent"]),
            "memory_percent": float(row["memory_percent"]),
            "available_memory_mb": float(row["available_memory_mb"])
        })

if not requests:
    print("No inference metrics found.")
    raise SystemExit

# Separate cold starts and warm requests
cold_starts = []
warm_requests = []

for request in requests:
    if request["load_seconds"] > 0.1:
        cold_starts.append(request)
    else:
        warm_requests.append(request)

# Latency analysis
total_durations = [request["total_seconds"] for request in requests]
total_durations.sort()

average = sum(total_durations) / len(total_durations)
fastest = min(total_durations)
slowest = max(total_durations)

p95_index = math.ceil(0.95 * len(total_durations)) - 1
p95_latency = total_durations[p95_index]

# Cold-start vs. warm-request latency
cold_latencies = [request["total_seconds"] for request in cold_starts]
warm_latencies = [request["total_seconds"] for request in warm_requests]

average_cold = sum(cold_latencies) / len(cold_latencies) if cold_latencies else 0
average_warm = sum(warm_latencies) / len(warm_latencies) if warm_latencies else 0

# Overall prompt processing throughput
total_prompt_tokens = sum(request["prompt_tokens"] for request in requests)
total_prompt_time = sum(request["prompt_duration_seconds"] for request in requests)

prompt_tokens_per_second = (
    total_prompt_tokens / total_prompt_time
    if total_prompt_time > 0 else 0
)

# Overall generation throughput
total_generation_tokens = sum(request["generation_tokens"] for request in requests)
total_generation_time = sum(request["generation_duration_seconds"] for request in requests)

generation_tokens_per_second = (
    total_generation_tokens / total_generation_time
    if total_generation_time > 0 else 0
)

# System resource analysis
average_cpu_before = sum(
    request["cpu_before"] for request in requests
) / len(requests)

average_cpu_after = sum(
    request["cpu_after"] for request in requests
) / len(requests)

average_memory = sum(
    request["memory_percent"] for request in requests
) / len(requests)

average_available_memory = sum(
    request["available_memory_mb"] for request in requests
) / len(requests)

# Display results
print(f"Requests analyzed: {len(requests)}")
print(f"Cold starts: {len(cold_starts)}")
print(f"Warm requests: {len(warm_requests)}")

print(f"\nAverage cold-start latency: {average_cold:.2f} seconds")
print(f"Average warm-request latency: {average_warm:.2f} seconds")

print(f"\nAverage latency: {average:.2f} seconds")
print(f"Fastest request: {fastest:.2f} seconds")
print(f"Slowest request: {slowest:.2f} seconds")
print(f"P95 latency: {p95_latency:.2f} seconds")

print(f"\nTotal prompt tokens: {total_prompt_tokens}")
print(f"Prompt processing throughput: {prompt_tokens_per_second:.2f} tokens/sec")

print(f"\nTotal generated tokens: {total_generation_tokens}")
print(f"Generation throughput: {generation_tokens_per_second:.2f} tokens/sec")

print("\nSystem Resource Analysis:")
print(f"Average CPU before inference: {average_cpu_before:.2f}%")
print(f"Average CPU after inference: {average_cpu_after:.2f}%")
print(f"Average memory utilization: {average_memory:.2f}%")
print(f"Average available memory: {average_available_memory:.0f} MB")

# Performance by prompt length
print("\nPerformance by prompt length:")

prompt_lengths = sorted(set(
    request["prompt_tokens"] for request in requests
))

for length in prompt_lengths:
    group = [
        request for request in requests
        if request["prompt_tokens"] == length
    ]

    average_latency = sum(
        request["total_seconds"] for request in group
    ) / len(group)

    total_prompt_tokens_group = sum(
        request["prompt_tokens"] for request in group
    )

    total_prompt_time_group = sum(
        request["prompt_duration_seconds"] for request in group
    )

    total_output_tokens_group = sum(
        request["generation_tokens"] for request in group
    )

    total_generation_time_group = sum(
        request["generation_duration_seconds"] for request in group
    )

    prompt_speed = (
        total_prompt_tokens_group / total_prompt_time_group
        if total_prompt_time_group > 0 else 0
    )

    generation_speed = (
        total_output_tokens_group / total_generation_time_group
        if total_generation_time_group > 0 else 0
    )

    print(f"\nPrompt size: {length} tokens")
    print(f"Requests: {len(group)}")
    print(f"Average latency: {average_latency:.2f} seconds")
    print(f"Prompt processing speed: {prompt_speed:.2f} tokens/sec")
    print(f"Generation speed: {generation_speed:.2f} tokens/sec")
