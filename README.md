# MTR-Bench: A Comprehensive Benchmark for Multi-Turn Reasoning Evaluation

[![Paper](https://img.shields.io/badge/paper-arXiv:2505.17123-red)](https://arxiv.org/abs/2505.17123)

## Introduction

This is the official repository for the paper **[MTR-Bench: A Comprehensive Benchmark for Multi-Turn Reasoning Evaluation](https://arxiv.org/abs/2505.17123)**.

While Large Language Models (LLMs) have shown remarkable progress in single-turn reasoning, their ability to handle complex, interactive tasks that require sustained, multi-turn reasoning remains largely unexplored. This gap is primarily due to the lack of comprehensive benchmarks and scalable evaluation protocols.

To bridge this gap, we present **MTR-Bench**, a novel framework designed to evaluate the multi-turn reasoning capabilities of LLMs. This repository provides:
1.  The complete **MTR-Bench** dataset, featuring 40 tasks across 4 reasoning categories.
2.  A fully **automated evaluation framework** (Generator, Monitor, Evaluator) that enables scalable, human-free assessment.
3.  Scripts and instructions to reproduce the extensive experiments on 20 reasoning-focused and general-purpose LLMs.

## ✨ Key Features

*   **Comprehensive Reasoning Coverage**: MTR-Bench includes 40 distinct tasks across 4 major reasoning classes: **Inductive, Abductive, Deductive, and Planning**.
*   **Fully-Automated Framework**: Our `Generator-Monitor-Evaluator` architecture automates the entire evaluation pipeline, from problem generation to final scoring, eliminating the need for human intervention.
*   **Scalable and Dynamic Difficulty**: The `Generator` can create a virtually infinite number of problems with finely-tuned difficulty levels (Easy, Medium, Hard), ensuring the benchmark remains challenging as models advance.
*   **In-depth Evaluation Metrics**: We assess models not just on **Accuracy**, but also on **Efficiency**, **Invalid Rate**, and **Reasoning Pattern Analysis**, providing a holistic view of their performance.
*   **Reproducible Research**: All scripts and configurations are provided to fully reproduce the findings and analysis presented in our paper.

## 📊 Benchmark Overview

MTR-Bench is structured around four core task categories, each designed to probe a specific facet of reasoning. These tasks necessitate multi-turn interaction, where models must actively query an environment, process feedback, and iteratively refine their strategy to succeed.

| Task Category               | Description                                                                     | Core Reasoning Skill  | Example Task       |
| --------------------------- | ------------------------------------------------------------------------------- | --------------------- | ------------------ |
| **Information Probing (IP)**  | Discover hidden, static information by collecting clues through queries.        | **Inductive Reasoning** | Find the Impostors |
| **Dynamic Adaptation (DA)**   | Track a target that changes based on deterministic rules after each interaction.| **Abductive Reasoning** | Password Breaker   |
| **State Operation (SO)**      | Infer hidden environmental mechanics (e.g., swapped controls) through actions.  | **Deductive Reasoning** | Maze Navigation    |
| **Strategic Gaming (SG)**     | Outperform a system-controlled opponent in an adversarial environment.          | **Planning**            | Knight Battle      |

## 🚀 Quick Start


#### Evaluating an Open-Source Model (e.g., Llama-3.1-70B)

```bash
python gen_model_answer.py --model-path /cpfs01/user/lanlin.lxy/models/Qwen2.5-1.5B-Instruct --model-id Qwen2.5-1.5B-Instruct --category information_query --game-type BitQuery  --difficulty easy --max-round 5 
```
## Citation

If you use MTR-Bench or our framework in your research, please cite our paper:

```bibtex
@misc{li2025mtrbench,
      title={MTR-Bench: A Comprehensive Benchmark for Multi-Turn Reasoning Evaluation}, 
      author={Xiaoyuan Li and Keqin Bao and Yubo Ma and Moxin Li and Wenjie Wang and Rui Men and Yichang Zhang and Fuli Feng and Dayiheng Liu and Junyang Lin},
      year={2025},
      eprint={2505.17123},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
