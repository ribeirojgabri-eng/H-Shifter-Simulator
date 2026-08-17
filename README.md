# H-Shifter-Simulator

### Real-Time Vehicle Powertrain & H-Pattern Transmission Simulation

A real-time vehicle powertrain simulation developed in **Python and Pygame**, evolving from an initial Hall sensor and RPM measurement concept into an interactive drivetrain model.

The project focuses on modeling the relationship between **engine speed, clutch engagement, transmission ratios, wheel torque, vehicle velocity, and longitudinal dynamics**.

> **From measuring RPM to understanding where that RPM goes.**

---

## Overview

This project started as an experimental study of RPM measurement using a Hall-effect sensor and evolved into a software-based vehicle powertrain simulator.

The current version provides an interactive environment where the user can operate a simulated manual transmission while the program calculates engine RPM, clutch behavior, wheel torque, vehicle acceleration, and vehicle speed in real time.

The simulator is designed primarily as an **engineering and educational project**, providing a practical environment for studying the interaction between mechanical systems and computational models.

---

## Features

* Real-time engine RPM simulation
* Interactive H-pattern manual transmission
* Six forward gears and reverse
* Clutch engagement and disengagement
* Engine idle and stall behavior
* Simplified engine torque model
* Gearbox and final-drive torque multiplication
* Wheel torque and tractive force calculation
* Longitudinal vehicle dynamics
* Aerodynamic drag approximation
* Rolling resistance approximation
* Engine braking
* Reverse-direction vehicle dynamics
* Real-time Pygame visualization

---

## System Architecture

The current simulation follows the simplified powertrain flow:

              ┌─────────────────┐
              │   Engine Model  │
              │  Torque / RPM   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     Clutch      │
              │   Engagement    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Transmission  │
              │   Gear Ratio    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Final Drive   │
              │   Differential  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Wheel Torque  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Tractive Force  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Vehicle Motion  │
              │ v / a / forces  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Transmission    │
              │      RPM        │
              └─────────────────┘
```

The vehicle state is continuously fed back into the powertrain model through the relationship between vehicle speed and drivetrain rotational speed.

---

## Engineering Model

### Vehicle Parameters

The current prototype uses the following primary parameters:

| Parameter             |    Value |
| --------------------- | -------: |
| Vehicle mass          |  1240 kg |
| Wheel radius          |   0.32 m |
| Final drive ratio     |     3.27 |
| Maximum engine speed  | 6500 RPM |
| Idle speed            |  900 RPM |
| Stall threshold       |  650 RPM |
| Drivetrain efficiency |      88% |

The transmission currently uses:

| Gear    | Ratio |
| ------- | ----: |
| 1st     |  3.83 |
| 2nd     |  2.36 |
| 3rd     |  1.55 |
| 4th     |  1.16 |
| 5th     |  0.92 |
| 6th     |  0.75 |
| Reverse | -3.50 |

The negative reverse ratio allows the direction of the drivetrain force to be represented directly through the mathematical model.

---

## Torque & Drivetrain Model

The engine currently uses a simplified mathematical torque curve.

The resulting engine torque is transmitted through the clutch and multiplied by the selected gear and final-drive ratios:

```text
Wheel Torque =
Engine Torque
× Clutch Engagement
× Gear Ratio
× Final Drive
× Drivetrain Efficiency
```

The resulting wheel torque is converted into tractive force using the wheel radius:

```text
Tractive Force = Wheel Torque / Wheel Radius
```

## This model is intentionally simplified and is intended for simulation and educational purposes rather than representing a production-engine torque map.

## Longitudinal Dynamics

The vehicle model calculates the net longitudinal force acting on the vehicle.

The current model includes:

* Tractive force
* Aerodynamic resistance
* Rolling resistance
* Engine braking

The resulting acceleration is calculated from:

```text
a = F_net / m
```

where:

* `a` = vehicle acceleration
* `F_net` = net longitudinal force
* `m` = vehicle mass

Vehicle velocity is then numerically integrated over time.

The resistance forces are applied according to the direction of vehicle motion, allowing the same model to handle both forward and reverse movement.

---

## Engine RPM Synchronization

When the clutch is engaged and a gear is selected, engine RPM is coupled to the rotational speed imposed by the vehicle drivetrain.

The transmission-side RPM is calculated from:

RPM =
|Vehicle Speed|
× 60
× |Gear Ratio|
× Final Drive
--------------------------------
2π × Wheel Radius
```

The simulator then progressively synchronizes the engine state with the drivetrain state.

This allows the model to reproduce behaviors such as:

* Engine lugging
* RPM drop during clutch engagement
* Engine acceleration during throttle input
* Engine braking
* Stall conditions

---

## Clutch Model

The clutch is represented by a normalized engagement state:

```text
0.0 → Fully disengaged
1.0 → Fully engaged
```

The user can temporarily disengage the clutch while selecting a gear through the interactive control system.

The model also introduces clutch slip during engagement, allowing engine RPM and drivetrain RPM to temporarily differ.

---

## Stall Detection

The simulator includes a simplified mechanical stall model.

When engine RPM falls below the defined stall threshold while the clutch is sufficiently engaged, the program estimates the minimum vehicle speed required to maintain engine operation.

If the vehicle cannot sustain that speed, the engine is switched off.

This mechanism is applied to both forward and reverse operation.

---

## Controls

| Input   | Function          |
| ------- | ----------------- |
| `SPACE` | Throttle          |
| `CTRL`  | Clutch            |
| `Mouse` | H-pattern shifter |
| `E`     | Engine ignition   |

### Shifting

1. Hold `CTRL` to disengage the clutch.
2. Move the mouse to the desired gear position.
3. Release `CTRL` to engage the clutch.
4. Use `SPACE` to apply throttle.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/H-Shifter-Simulator.git
cd H-Shifter-Simulator
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```
.venv\Scripts\activate
```

### Linux / macOS

```
source .venv/bin/activate
```

Install the dependencies:

```
pip install -r requirements.txt
```

---

## Running the Simulator

```
python src/Simulator.py
```

The simulator opens a real-time Pygame interface displaying:

* Vehicle speed
* Engine RPM
* Current gear
* Clutch engagement
* RPM gauge
* Interactive H-pattern shifter

---

## Current Project Status

### Implemented

* [x] Real-time simulation loop
* [x] Engine RPM model
* [x] Simplified engine torque model
* [x] Manual transmission model
* [x] H-pattern interaction
* [x] Clutch engagement
* [x] Gear ratios
* [x] Final drive
* [x] Wheel torque calculation
* [x] Longitudinal vehicle dynamics
* [x] Aerodynamic resistance
* [x] Rolling resistance
* [x] Engine braking
* [x] Reverse-direction dynamics
* [x] Stall detection
* [x] Real-time visualization

### In Development

* [ ] Modular software architecture
* [ ] Automated unit tests
* [ ] Improved engine torque model
* [ ] Improved clutch model
* [ ] Tire model
* [ ] Gearbox inertia
* [ ] Data logging
* [ ] Simulation result plots
* [ ] Hall-effect sensor hardware integration

---

## Known Limitations

This project is a simplified engineering model and does not attempt to reproduce the complete behavior of a real vehicle.

Current limitations include:

* Simplified engine torque curve
* Simplified clutch dynamics
* No tire slip model
* No detailed gearbox inertia model
* No thermal effects
* No suspension dynamics
* No lateral vehicle dynamics
* No detailed aerodynamic model
* No physical sensor input in the current prototype

These limitations are intentional development boundaries and provide the basis for future model improvements.

---

## Development Roadmap

The project is being progressively developed toward a more modular and physically representative simulation architecture.

### Phase 1 — Functional Prototype

* Real-time powertrain simulation
* H-pattern transmission
* Basic vehicle dynamics

### Phase 2 — Software Architecture

* Modular physics components
* Configuration management
* Automated testing
* Data logging

### Phase 3 — Model Refinement

* Improved engine model
* Clutch torque-transfer model
* Tire behavior
* Gearbox dynamics

### Phase 4 — Hardware Integration

* Hall-effect sensor input
* Real RPM acquisition
* Physical control interface

### Phase 5 — Validation

* Experimental measurements
* Simulation vs. experimental comparison
* Parameter identification
* Model calibration

---

## Project Structure

```text
H-Shifter-Simulator/
│
├── src/
│   └── Simulator.py
│
├── docs/
│   ├── architecture.md
│   ├── physics.md
│   ├── transmission.md
│   └── development-log.md
│
├── assets/
│   └── screenshots/
│
├── tests/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## Engineering Philosophy

The purpose of this project is not simply to make a vehicle *look* simulated.

It is to build a computational model where the behavior of the vehicle can be traced back to identifiable physical assumptions and mathematical relationships.

The development process therefore follows:


Physical Problem
       ↓
Assumptions
       ↓
Mathematical Model
       ↓
Software Implementation
       ↓
Simulation
       ↓
Validation
       ↓
Iteration
```

As the project evolves, increasingly complex models will replace simplified assumptions.

---

## Author

**João Gabriel Pereira Ribeiro**

Mechatronics Engineering student focused on automotive engineering, simulation, programming, and prototyping.

---

## License

This project is released under the MIT License.
