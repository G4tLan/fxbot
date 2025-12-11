# Architecture Overview

## Introduction
A Python-based trading framework designed for simplicity and power. It serves as the backend engine that handles backtesting, live trading, optimization, and data importation. It is designed to be controlled via a frontend dashboard (API-driven) or CLI.

## High-Level Architecture

The system is organized into four main layers:

1.  **[API / Interface Layer](api_layer/overview.md)**: The entry point for external interaction (Dashboard/CLI). It handles HTTP requests and WebSocket connections.
2.  **[Execution Layer (Modes)](execution_layer/overview.md)**: The engines that run specific tasks. Whether it's a historical simulation (Backtest) or real-time trading (Live), this layer orchestrates the flow.
3.  **[Strategy Layer](strategy_layer/overview.md)**: The user-facing logic. This is where trading strategies, indicators, and rules are defined.
4.  **[Core Infrastructure](core_infrastructure/overview.md)**: The foundation. Includes database models, configuration management, storage, and utility services.

## Supporting Layers

In addition to the main layers, there are specialized components:

- **[Exchange Adapters](supporting_layers/exchange_adapters.md)**: Abstractions for connecting to different exchanges (including the Sandbox).
- **[Research Tools](supporting_layers/research_tools.md)**: Utilities for Jupyter notebooks and quantitative analysis.
- **[Factories](supporting_layers/factories.md)**: Generators for synthetic data used in testing.

## Data Flow

1.  **Command**: A user initiates an action (e.g., "Start Backtest") via the Dashboard.
2.  **Routing**: The **API Layer** receives the request and routes it to the appropriate Controller.
3.  **Process**: The Controller spawns a new process via the Process Manager to run the specific **Execution Mode**.
4.  **Simulation/Run**: The **Execution Layer** loads necessary data (candles) and initializes the **Strategy Layer**.
5.  **Loop**: The system iterates through time (historical or real-time), feeding data into the Strategy.
6.  **Action**: The Strategy makes decisions (buy/sell), which are executed by the simulated or real exchange adapter.
7.  **Feedback**: Results and logs are stored in the **Core Infrastructure** (Database/Files) and streamed back to the UI via WebSockets.

## Directory Structure Mapping

- `engine/` - Main package
    - `__init__.py` - API Entry point
    - `controllers/` - API Controllers
    - `modes/` - Execution Engines (Backtest, Import, etc.)
    - `strategies/` - Base Strategy Logic
    - `models/` - Database Models
    - `services/` - Core Services (DB, Redis, etc.)
