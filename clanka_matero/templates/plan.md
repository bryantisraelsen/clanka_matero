# Clanka Matero - Web UI implementation plan

## Introduction

This webapp will be used to control a robotic hot-water dispenser known affectionatly as "Clanka Matero".

Users will be able to monitor the status of Clanka Matero as well as interact with him.

This webapp should be usable from both desktop and mobile, with a focus on mobile.

## Montioring

Users should be able to monitor the following:
- Current Temperature of the Water
- Whether the heater is on
- Whether the "keep warm" function is on
- Whether there is enough water in the system to run the heater


## Control

Users should be able to control the following:
- Desired water temperature
- Time in seconds for automatic water dispersal
- Status of the auto heat (on/off)
- Dispense (users can start a timed dispense from the webapp)

## Implementation details

- Single page application
- Support for dark/light mode
- Monitoring will be polled periodically using javascript
- Frontend will be rendered via flask templates