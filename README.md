# Local AI Inference & Observability Platform

A locally hosted AI inference platform built with Python and Ollama, designed to explore LLM deployment, API integration, performance benchmarking, resource monitoring, and infrastructure reliability.

## Overview

This project explores the infrastructure behind running and monitoring large language models locally.

Using Ollama to serve an open-source language model, a custom Python client communicates with the inference API, measures request performance, monitors system resources, handles failures, and records metrics for later analysis.

The long-term goal is to develop a locally operated inference platform with observability, retrieval-augmented generation (RAG), and deployment capabilities.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Client implementation, benchmarking, and metrics analysis |
| Ollama | Local LLM runtime and inference API |
| Qwen 2.5 1.5B | Open-source language model |
| HTTP / REST | Communication with the inference server |
| JSON | Request and response serialization |
| CSV | Persistent inference metrics storage |
| psutil | CPU and memory utilization monitoring |
| Git / GitHub | Version control and project hosting |

## Current Implementation

- Downloaded and configured Qwen 2.5 1.5B for local CPU inference.
- Built a Python client using HTTP requests to communicate with Ollama's REST API.
- Implemented HTTP error handling, connection error handling, and request timeouts.
- Implemented batch inference benchmarking across multiple requests.
- Captured prompt processing time, generation time, total inference duration, and token throughput.
- Recorded input and output token counts for each inference request.
- Implemented cold-start and warm-request classification.
- Collected system-wide CPU utilization and memory usage measurements using psutil.
- Persisted timestamped inference and resource metrics to CSV.
- Developed a separate analysis script to calculate average latency, fastest and slowest requests, P95 latency, aggregate token throughput, and resource utilization.
- Analyzed performance across different prompt lengths.
- Initialized Git version control and published the project to GitHub.

## Planned Development

- [x] Local LLM installation and inference
- [x] Python REST API client
- [x] Error handling and request timeouts
- [x] Batch inference benchmarking
- [x] Inference performance metrics collection
- [x] CSV-based metrics persistence
- [x] CPU and memory resource monitoring
- [x] Benchmark analysis and latency statistics
- [ ] FastAPI inference service
- [ ] Streaming inference support
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] Prometheus and Grafana observability
- [ ] Docker containerization
- [ ] Automated testing and CI/CD

## Running Locally

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/)
- Qwen 2.5 1.5B model

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/marioesc425/local-ai-inference-platform.git
   cd local-ai-inference-platform
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required Python dependency:

   ```bash
   pip install -r requirements.txt
   ```

4. Download the model:

   ```bash
   ollama pull qwen2.5:1.5b
   ```

5. Ensure Ollama is running, then execute the inference benchmark:

   ```bash
   python3 ollama_client.py
   ```

6. Analyze the collected benchmark results:

   ```bash
   python3 analyze_metrics.py
   ```

The client communicates with the local Ollama server at `http://localhost:11434` and records inference metrics in `inference_metrics.csv`.

## Metrics and Observability

The benchmarking client collects:

| Metric | Description |
|---|---|
| Total inference duration | Time spent processing the request inside Ollama |
| Model load duration | Time spent loading the model |
| Prompt evaluation duration | Time spent processing input tokens |
| Generation duration | Time spent generating output tokens |
| Prompt throughput | Input tokens processed per second |
| Generation throughput | Output tokens generated per second |
| Client elapsed time | Total request time measured by the Python client |
| CPU utilization | System-wide CPU utilization snapshots |
| Memory utilization | System-wide memory utilization |
| Available memory | Available system RAM in megabytes |

The analysis script calculates aggregate performance statistics, including average latency, P95 latency, cold-start versus warm-request latency, and overall token throughput.

**Monitoring limitation:** CPU and memory measurements are system-wide snapshots rather than continuous, process-specific measurements. GPU utilization is not currently monitored.