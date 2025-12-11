# Core Infrastructure

[← Back to Architecture Overview](../architecture_overview.md)

## Overview
This layer supports the entire application, handling data persistence, configuration, and low-level utilities. It provides the foundation upon which the Execution and Strategy layers are built.

## Components

### 1. [Database & Models](database_models.md)
Documentation for the data layer, including the Peewee ORM models for Candles, Trades, and Orders.

### 2. [Configuration](configuration.md)
Details on how the system is configured, including the global `config` dictionary and environment settings.

### 3. [Storage](storage.md)
Explanation of the file-based storage system for logs, exports, and local databases.

### 4. [Services & Utilities](services_utilities.md)
Overview of the core services (Broker, Logger, Process Manager) and helper functions that power the application.
