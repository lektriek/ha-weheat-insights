# Changelog

All notable changes to Weheat Insights are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/). Each version's section becomes the
notes of its GitHub release, which HACS shows when offering the update.

## [Unreleased]

### Changed

- Release notes now come from this changelog instead of a list of commits.

## [0.9.1] - 2026-11-24

### Fixed

- Setup no longer fails with "too many values to unpack" when another
  integration registers devices with unusual identifiers (#1).

## [0.9.0] - 2026-11-23

### Added

- Hot-water tab: the Weheat Intelligence plan of yesterday, today and
  tomorrow, planned against actual heating, and the plan's target against the
  heat pump's. Shown only when Weheat Control is installed and a plan is
  available.
- Sensors for hot-water activity (none, hot water, legionella prevention) and
  for the plan's target temperature.

## [0.8.5] - 2026-11-23

### Changed

- Supply now means the water going into the heating system, for the dashboard,
  the ΔT sensor, the supply curve and the heating-curve advice. The heat pump
  outlet is shown apart. Heat pumps without that sensor use the outlet as
  before (#2).

## [0.8.4] - 2026-11-12

### Changed

- Dutch texts and cards use degrees instead of kelvin, and "per uur".
- The project moved to the lektriek organisation on GitHub.

## [0.8.3] - 2026-11-12

### Changed

- Hot water: the COP fit is corrected for the other temperature, with
  legionella prevention apart; the set target is left out of the heated-to
  chart.
- Live: shows the supply target, and the room target only when the thermostat
  has one.

## [0.8.2] - 2026-11-12

### Fixed

- Hot water: a run interrupted by heating or defrost counts once.
- Hot water: no "heated to today" before today's first run.
- Hot water: only clearly hotter days count as legionella prevention.

### Changed

- Hot water: shorter summary note, with the explanation as a list.

## [0.8.1] - 2026-11-12

### Fixed

- Hot water: "heated to" is the real daily maximum, legionella prevention
  included, and the daily set target is the lowest one, so legionella
  prevention does not show there.

## [0.8.0] - 2026-11-12

### Added

- Hot-water tab: tank target per day, COP against tank and outdoor
  temperature, run start times and standing loss, with Home Assistant bar
  charts.

## [0.7.5] - 2026-11-12

### Added

- Live: the thermostat's target temperature next to the room temperature.

### Changed

- Operation tab: the state timeline comes first; standby is left out of hours
  per day and crowded charts are split.

## [0.7.4] - 2026-11-11

### Changed

- COP tiles use your decimal separator.
- The heat-loss line is cut off at the edges of the plot.
- README screenshots.

## [0.7.3] - 2026-11-11

### Fixed

- The explanation card fills its two-column section.

## [0.7.2] - 2026-11-11

### Changed

- Time counters include running periods; the curve chart stops at 25 °C;
  explanations are wider.

## [0.7.1] - 2026-11-11

### Added

- Legionella prevention in the Operation per-day charts.

## [0.7.0] - 2026-11-11

### Added

- Enter your current heating curve; the date it changed is stored
  automatically.

## [0.6.11] - 2026-11-11

### Removed

- The current-curve column of the advice table.

## [0.6.10] - 2026-11-11

### Fixed

- Days without heating are left out of the heat-loss fit.

## [0.6.9] - 2026-11-11

### Fixed

- The first period of statistics is correct when there is history before it.

## [0.6.8] - 2026-11-11

### Changed

- Heating-curve advice is calibrated on 12 months of history.

## [0.6.7] - 2026-11-11

### Changed

- Operating counts are shown as "4×".

## [0.6.6] - 2026-11-11

### Changed

- One operating-statistics card instead of two tables, and a dot for the
  current curve.

## [0.6.5] - 2026-11-11

### Changed

- Legionella prevention is counted as such instead of as "other".

## [0.6.4] - 2026-11-11

### Fixed

- Table cards span their whole section.

## [0.6.3] - 2026-11-11

First published release, with everything built up in the versions before it:

### Added

- A ready-made dashboard with Live, Performance, House, Heating curve and
  Operation tabs, and cards for your own dashboards.
- COP and SCOP, defrost, degree-day and heat-per-degree-day sensors, with
  degree days as a long-term statistic and a configurable heating season.
- House analysis: heat loss and cool-down.
- Heating-curve advice with a before/after comparison.
- Operating-state sensors and statistics.
- Supply/return ΔT sensor.

[Unreleased]: https://github.com/lektriek/ha-weheat-insights/compare/v0.9.1...HEAD
[0.9.1]: https://github.com/lektriek/ha-weheat-insights/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.5...v0.9.0
[0.8.5]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.4...v0.8.5
[0.8.4]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.3...v0.8.4
[0.8.3]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/lektriek/ha-weheat-insights/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.5...v0.8.0
[0.7.5]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.4...v0.7.5
[0.7.4]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.3...v0.7.4
[0.7.3]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.2...v0.7.3
[0.7.2]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.1...v0.7.2
[0.7.1]: https://github.com/lektriek/ha-weheat-insights/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.11...v0.7.0
[0.6.11]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.10...v0.6.11
[0.6.10]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.9...v0.6.10
[0.6.9]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.8...v0.6.9
[0.6.8]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.7...v0.6.8
[0.6.7]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.6...v0.6.7
[0.6.6]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.5...v0.6.6
[0.6.5]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.4...v0.6.5
[0.6.4]: https://github.com/lektriek/ha-weheat-insights/compare/v0.6.3...v0.6.4
[0.6.3]: https://github.com/lektriek/ha-weheat-insights/releases/tag/v0.6.3
