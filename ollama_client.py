
import urllib.request
import json
import time
import urllib.error
import csv
import psutil
from datetime import datetime

CALLS = 10

timeout = 30
url = "http://localhost:11434/api/generate"

prompt = input("Enter your prompt: ")

data = {
    "model": "qwen2.5:1.5b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": 100
    }
}

json_data = json.dumps(data).encode("utf-8")

# Run inference requests
for i in range(CALLS):
    print(f"\nRunning request {i + 1}/{CALLS}")

    request = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    timestamp = datetime.now().isoformat(timespec="seconds")

    # Capture system resources before inference
    cpu_before = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    available_memory_mb = memory.available / (1024 * 1024)

    start_time = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_data = response.read()
            response_text = response_data.decode("utf-8")
            result = json.loads(response_text)

            elapsed_time = time.perf_counter() - start_time

            # Capture CPU utilization after inference
            cpu_after = psutil.cpu_percent(interval=0.1)

            # Generation speed
            tokens_per_second = (
                result["eval_count"] /
                (result["eval_duration"] / 1_000_000_000)
            )

            # Prompt processing speed
            prompt_tokens_per_second = (
                result["prompt_eval_count"] /
                (result["prompt_eval_duration"] / 1_000_000_000)
            )

            print(result["response"])
            print(f"Input tokens: {result['prompt_eval_count']}")
            print(f"Output tokens: {result['eval_count']}")
            print(f"Request completed in {elapsed_time:.2f} seconds")
            print(f"Prompt processing speed: {prompt_tokens_per_second:.2f} tokens/sec")
            print(f"Generation speed: {tokens_per_second:.2f} tokens/sec")

            # Display system resource metrics
            print(f"CPU before inference: {cpu_before:.1f}%")
            print(f"CPU after inference: {cpu_after:.1f}%")
            print(f"Memory utilization: {memory_percent:.1f}%")
            print(f"Available memory: {available_memory_mb:.0f} MB")

            metrics = [
                timestamp,
                result["total_duration"],
                result["load_duration"],
                result["prompt_eval_duration"],
                result["prompt_eval_count"],
                result["eval_duration"],
                result["eval_count"],
                prompt_tokens_per_second,
                tokens_per_second,
                elapsed_time,
                cpu_before,
                cpu_after,
                memory_percent,
                available_memory_mb
            ]

            with open("inference_metrics.csv", "a", newline="") as file:
                writer = csv.writer(file)

                if file.tell() == 0:
                    writer.writerow([
                        "timestamp",
                        "total_duration_ns",
                        "load_duration_ns",
                        "prompt_eval_duration_ns",
                        "prompt_eval_count",
                        "eval_duration_ns",
                        "eval_count",
                        "prompt_tokens_per_second",
                        "generation_tokens_per_second",
                        "elapsed_seconds",
                        "cpu_before_percent",
                        "cpu_after_percent",
                        "memory_percent",
                        "available_memory_mb"
                    ])

                writer.writerow(metrics)

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.reason)

    except TimeoutError:
        print("Request timed out. Ollama took too long to respond.")

    except urllib.error.URLError as e:
        print("Connection error: Unable to reach Ollama.")
