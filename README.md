# Local AI Inference & Observability Platform

A locally hosted AI inference platform built with Python and Ollama, designed to explore LLM deployment, API integration, performance monitoring, and infrastructure reliability.

## Overview

This project explores the infrastructure behind running and monitoring large language models locally.

Using Ollama to serve an open-source language model, a custom Python client communicates with the inference API, measures request performance, handles failures, and records metrics for later analysis.

The long-term goal is to develop a locally operated inference platform with observability, retrieval-augmented generation (RAG), and deployment capabilities.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Client implementation and metrics collection |
| Ollama | Local LLM runtime and inference API |
| Qwen 2.5 1.5B | Open-source language model |
| HTTP / REST | Communication with the local inference server |
| JSON | Request and response serialization |
| CSV | Persistent inference metrics storage |
| Git / GitHub | Version control and project hosting |

## Current Implementation

- Downloaded and configured Qwen 2.5 1.5B for local CPU inference.
- Built a Python client using the standard library to communicate with Ollama's REST API.
- Implemented HTTP error handling, connection error handling, and request timeouts.
- Measured inference duration, model loading time, generation time, and token throughput.
- Persisted timestamped inference metrics to CSV.
- Initialized Git version control and published the project to GitHub.

## Planned Development

- [x] Local LLM installation and inference
- [x] Python REST API client
- [x] Error handling and request timeouts
- [x] Inference performance metrics collection
- [x] CSV-based metrics persistence
- [ ] FastAPI inference service
- [ ] Streaming inference support
- [ ] Resource utilization monitoring (CPU and memory)
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] Prometheus and Grafana observability
- [ ] Docker containerization
- [ ] Automated testing and CI/CD

## Running Locally

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com/)

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

3. Download the model:

   ```bash
   ollama pull qwen2.5:1.5b
   ```

4. Run the inference client:

   ```bash
   python ollama_client.py
   ```

The client communicates with the local Ollama server at `http://localhost:11434` and records inference metrics in `inference_metrics.csv`.
