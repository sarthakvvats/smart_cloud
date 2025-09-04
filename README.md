# Intelligent Cloud Storage Tier Optimization using Reinforcement Learning

This project presents a hybrid approach to cloud storage optimization by leveraging Reinforcement Learning (PPO) and access pattern prediction, optimized for both latency and cost. It operates on both synthetic and real-world cloud workload data (Google trace subset from WTA) and includes comparative evaluations and cost-benefit visualizations.

## Key Features

- Reinforcement Learning (PPO) for adaptive tier placement
- Latency-aware and cost-aware reward function
- Three-tier simulation: Hot, Warm, and Cold (e.g., SSD to HDD to Archive)
- Synthetic and real-world trace compatibility
- Visual analytics: tier-wise distribution, total cost, per-file cost margin
- Designed for research-grade cloud storage benchmarking

## Files Overview

- `Cloud.ipynb`: Main notebook for data ingestion, simulation, PPO logic, and visualizations
- `google_cluster_trace_25k.csv`: Subset of WTA Google trace (25,000 entries) used for evaluation
- `ppo_*_chart.png`: Bar and line plots comparing PPO vs original tiering
- `overall_cost_with_margin_chart.png`: Cost and file-volume comparison with margin annotations
- `ppo_reward.py`: Modular reward function for training PPO agents (optional for extension)

## Dataset

- Source: Workflow Trace Archive (WTA), https://wta.atlarge-research.com
- Subset: Google Cloud traces (25,000-object sample)
- Anonymized and preprocessed for storage-specific access simulation

## Cost Model (in INR)

- Cold Tier: ₹0.33 per GB, Latency: 500 ms
- Warm Tier: ₹0.825 per GB, Latency: 150 ms
- Hot Tier: ₹2.145 per GB, Latency: 20 ms

## Reward Function

The hybrid reward function used during PPO training:


This balances access needs with cost penalties using domain-aware tuning.

## Results Summary

- Total Cost Reduction: From ₹822.77 to ₹57.08
- Latency Efficiency: Approximately 45% of optimal hot-tier-only performance
- PPO dynamically adapts file placement based on both access patterns and cost constraints

## Visualizations

The repository includes:

- Tier-wise cost comparison
- File count vs tier allocation
- Normalized latency and savings distribution
- PPO vs Baseline (subset matched)

## Usage Instructions

1. Place `Cloud.ipynb` and `google_cluster_trace_25k.csv` in the working directory
2. Run the notebook step-by-step in Jupyter or Google Colab
3. All analysis results and charts will be generated automatically

## Possible Extensions

- Integrate LSTM-based access forecasting
- Scale PPO training using `stable-baselines3`
- Connect to live GCP or AWS S3 buckets for real-time decision-making

## License

This repository is intended for academic and research use only.

## Acknowledgements

- Workflow Trace Archive
- Google Cloud Trace dataset
- PPO agent design adapted from OpenAI Gym and Stable Baselines3
