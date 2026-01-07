# Artificial-Defect-Data-Driven-Training-of-LLMs-for-Fault-Localization

This repository implements a mutation-driven framework for **training large language models (LLMs) for fault localization** using **artificial defect data generated from real software projects**.

## Overview

Fault localization datasets with precise ground truth are scarce and expensive to construct.  
This project addresses this challenge by **systematically injecting artificial faults into project source files via mutation**, executing test suites to expose failures, and transforming the resulting artifacts into **supervised training data for LLM-based fault localization**.

Rather than relying on inference-time prompting alone, the framework explicitly **trains LLMs** to localize faults using mutation-based defect instances grounded in real project structure and test behavior.

## Key Idea

> **Train LLMs for fault localization using mutation-based defect data with known ground-truth fault locations.**

## High-Level Pipeline

1. **Mutation-Based Fault Injection**  
   Apply fine-grained code mutations to real project source files to introduce artificial faults.

2. **Failure Validation & Data Collection**  
   Execute test suites to confirm fault-revealing mutations and collect failing tests, coverage, and mutation metadata.

3. **Training Data Construction**  
   Convert each validated mutation into a labeled fault-localization instance with precise ground truth.

4. **LLM Training**  
   Fine-tune LLMs (e.g., via LoRA) using the mutation-based defect dataset.

5. **Evaluation**  
   Evaluate trained models using rank-based fault localization metrics (e.g., Acc@k).

## Why Mutation-Based Defect Data?

- Scalable generation of labeled defect instances  
- Precise and controllable ground-truth fault locations  
- Grounded in real project code and test behavior  
- Enables **training-time learning**, not just inference-time reasoning


## Status

Research prototype.  Designed for experimentation and extension in academic settings.
