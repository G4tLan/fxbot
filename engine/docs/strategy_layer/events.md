# Events

[← Back to Strategy Layer Overview](overview.md)

## Overview
Strategies can react to specific events during the lifecycle of a trade. These methods allow you to execute custom logic (logging, notifying, variable updates) when the state changes.

## Position Events

### `on_open_position(order)`
Called immediately after a position is opened (entry filled).
- **Usage**: Reset variables, log entry.

### `on_close_position(order)`
Called immediately after a position is closed.
- **Usage**: Calculate trade PnL, update stats.

### `on_increased_position(order)`
Called when the position size increases (pyramiding).

### `on_reduced_position(order)`
Called when the position size decreases (partial take-profit).

## Route Events
In multi-route strategies, you can react to events happening in *other* routes.

### `on_route_open_position(strategy)`
Called when another strategy in the same session opens a position.

### `on_route_close_position(strategy)`
Called when another strategy closes a position.

### `on_route_canceled(strategy)`
Called when another strategy cancels its orders.
