# Contributing to TPZ Competency Analyzer

Thank you for your interest in contributing to the TPZ Competency Analyzer! This document provides guidelines and information for contributors.

## Project Structure

This project is a TPZ-specific adaptation that combines two separate tools:

1. **Audio Reflection Module**: Based on CompExtractor by Gus Halwani ([@fizt656](https://github.com/fizt656/compextractor))
2. **Portfolio Analysis Module**: Created by Miles Baird ([@kilometers](https://github.com/kilometers/zs-portfolio))

The integration and TPZ-specific adaptations are maintained by The Possible Zone.

## Repository Organization

The repository is organized as follows:

- `src/` - Main source code directory
  - `main.py`, `config.py`, etc. - Core audio analysis functionality
  - `zonesight_gui.py` - Unified GUI for both modules
  - `portfolio/` - Portfolio analysis module
- `results/` - Output directory for analysis results
- `example_reports/` - Example output reports
- `temp/` - Temporary files (auto-cleaned after processing)

## Development Guidelines

### Setting Up Development Environment

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the required environment variables (see README.md)

### Making Changes

When making changes to the codebase, please consider the following:

1. **Audio Reflection Module**: Changes to the core audio analysis functionality should ideally be coordinated with the original CompExtractor repository.

2. **Portfolio Analysis Module**: Changes to the portfolio analysis functionality should ideally be coordinated with the original zs-portfolio repository.

3. **TPZ-Specific Adaptations**: Changes to TPZ-specific features (competency frameworks, reporting dimensions, etc.) should be reviewed by TPZ stakeholders.

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes thoroughly
5. Submit a pull request with a clear description of the changes

## Relationship with Original Projects

### Updates from Original Repositories

When incorporating updates from the original repositories:

1. **For Audio Reflection Module**:
   - Check for updates in the original CompExtractor repository
   - Evaluate if the updates are relevant for the TPZ adaptation
   - Adapt the changes to work with the integrated codebase

2. **For Portfolio Analysis Module**:
   - Check for updates in the original zs-portfolio repository
   - Evaluate if the updates are relevant for the TPZ adaptation
   - Adapt the changes to work with the integrated codebase

### Contributing Back to Original Projects

If you make improvements that could benefit the original projects:

1. Consider submitting pull requests to the original repositories
2. Ensure that TPZ-specific code is removed or abstracted appropriately
3. Coordinate with the original authors

## Code Style and Standards

- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation when making significant changes

## Questions and Support

If you have questions about contributing, please contact The Possible Zone:
https://www.possiblezone.org/contact
