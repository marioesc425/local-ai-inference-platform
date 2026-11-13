import urllib.request
import json
import time
import urllib.error
import csv
from datetime import datetime

timeout=30

## Our JSON body we plan to send
data = {
    "model": "qwen2.5:1.5b",
    "prompt": "Explain what an API is in three sentences.",
    "stream": False
}

## Convert dictionary into JSON bytes
json_data = json.dumps(data).encode("utf-8")

url = "http://localhost:11434/api/generate"

request = urllib.request.Request(
    url,
    data=json_data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

## Read Response
timestamp = datetime.now().isoformat(timespec="seconds")
start_time = time.perf_counter()

try:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_data = response.read()
        response_text = response_data.decode("utf-8")
        result = json.loads(response_text)
        print("Timestamp:", timestamp)
        print(result["response"])
        tokens_per_second = (
            result["eval_count"] /
            (result["eval_duration"] / 1_000_000_000)
        )

        print(f"Tokens per second: {tokens_per_second:.2f}")
        metrics = [
            timestamp,
            result["total_duration"],
            result["load_duration"],
            result["eval_duration"],
            result["eval_count"],
            tokens_per_second
        ]
        with open("inference_metrics.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow([
                    "timestamp",
                    "total_duration_ns",
                    "load_duration_ns",
                    "eval_duration_ns",
                    "eval_count",
                    "tokens_per_second"
                ])
            writer.writerow(metrics)

        elapsed_time = time.perf_counter() - start_time
        print(f"\nRequest completed in {elapsed_time:.2f} seconds")
        print("Total duration:", result["total_duration"])
        print("Model load duration:", result["load_duration"])
        print("Prompt evaluation duration:", result["prompt_eval_duration"])
        print("Generation duration:", result["eval_duration"])
        print("Generated tokens:", result["eval_count"])

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.reason)
except TimeoutError:
    print("Request timed out. Ollama took too long to respond.")
except urllib.error.URLError as e:
    print("Connection error: Unable to reach Ollama.")
