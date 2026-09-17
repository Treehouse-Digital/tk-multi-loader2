# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


These track the only functional differences between SG/upstream and our own fork.


## [1.25.6-th.1.2.0] - 2026-09-17

### Changed

- config:entities: `filters` now support ID expansion for all context attributes
  - Any string entirely matching `{context.<attribute>.id}` will be expanded to the corresponding context attribute's ID as integer.
  - Prioritised over below `format(context=app.context)` expansion.
- config:entities: `filters` and `entity_type` now expand `context` variable via Python string `format(context=app.context)`


## [1.25.6-th.1.1.0] - 2026-09-17

### Added

- `format_publishes` hook for customizing the formatting of folder/publish items' widget
    - Minimal for our own use, not fully test covered or documented for PR back to SG

### Changed

- Manual tag-to-release workflow to automatically create GitHub releases from `CHANGELOG.md` versions.

### Fixed

- Silenced unnecessary INFO log messages in `filter_publishes` hook.


## [1.25.6-th.1.0.1] - 2026-05-26

### Fixed

- Unnecessary executable permissions
- Removed conflicting custom pre-commit CI hook.


## [1.25.6-th.1.0.0] - 2026-05-26

### Added

- This CHANGELOG.md, CI for pre-commit and releasing upon tag


## [1.25.4-th.1.0.0] - 2025-11-14

### Added

- `publish_fields` settings for additional entity fields to fetch.
