# ADR 001: Add CMake Build System for Odoo Project Management

**Date:** 2025-10-23

**Status:** Accepted

## Context

The Odoo Educational ERP System project requires a standardized way to manage common development tasks such as:
- Configuring and initializing the database
- Updating Odoo modules
- Starting the Odoo server
- Managing development workflows

Currently, developers need to manually execute Python commands with specific parameters, which can lead to:
- Inconsistent command usage across the team
- Errors due to typos or incorrect parameters
- Lack of documentation for common tasks
- Difficulty onboarding new developers

The project structure includes:
- Custom `education_management` module
- Odoo core framework in the `odoo/` directory
- Configuration file `odoo.conf`
- Database name: `edu_demo_new`

## Decision

We will adopt **CMake** as a task runner and build system orchestrator for the Odoo project, despite Odoo being a Python-based application that doesn't require compilation.

### Implementation Details

A `CMakeLists.txt` file has been created at the project root with the following custom targets:

1. **`config_module`** - Configure database and update base module
   ```bash
   python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init
   ```

2. **`run`** - Start Odoo server manually
   ```bash
   python odoo/odoo-bin -c odoo.conf
   ```

3. **`update_module`** - Update specific custom modules (extensible)

### Usage

```bash
# Configure the project
cmake -B build

# Run targets
cmake --build build --target config_module
cmake --build build --target run
```

## Rationale

### Why CMake?

1. **Cross-platform compatibility** - Works on Windows, Linux, and macOS
2. **IDE integration** - Supported by Visual Studio Code, CLion, Visual Studio, and other IDEs
3. **Familiar tooling** - Many developers already know CMake
4. **Task orchestration** - Custom targets provide a clean interface for common tasks
5. **Documentation as code** - Commands are documented in the CMakeLists.txt file
6. **Extensibility** - Easy to add new targets for testing, deployment, etc.

### Alternatives Considered

1. **Make/Makefile**
   - ❌ Not cross-platform (requires additional tools on Windows)
   - ❌ Less IDE integration
   - ✅ Simpler syntax

2. **Shell scripts (bash/PowerShell)**
   - ❌ Platform-specific (need separate scripts for Windows/Unix)
   - ❌ No IDE integration
   - ✅ More flexible for complex logic

3. **Python scripts (invoke/fabric)**
   - ✅ Native to Python ecosystem
   - ❌ Additional dependency to manage
   - ❌ Less standardized across projects

4. **npm scripts (package.json)**
   - ❌ Requires Node.js (unnecessary dependency)
   - ❌ Not idiomatic for Python projects

5. **Just (command runner)**
   - ✅ Modern and simple
   - ❌ Less widespread adoption
   - ❌ Additional tool to install

## Consequences

### Positive

- **Standardized workflow** - All developers use the same commands
- **Self-documenting** - CMake configuration shows available targets and usage
- **IDE support** - Targets appear in IDE build menus
- **Reduced errors** - Centralized command definitions prevent typos
- **Easy onboarding** - New developers can see available commands immediately
- **Extensible** - Easy to add new targets for CI/CD, testing, deployment

### Negative

- **Learning curve** - Developers unfamiliar with CMake need to learn basic usage
- **Overhead** - CMake is primarily a build system, using it as a task runner is unconventional
- **Configuration step** - Requires initial `cmake -B build` before running targets
- **Not Python-native** - Adds a non-Python tool to a Python project

### Neutral

- **No compilation** - CMake's build features are unused; only custom targets are leveraged
- **Maintenance** - CMakeLists.txt needs updates when adding new common tasks

## Implementation Notes

- Python 3 interpreter is automatically detected via `find_package(Python3)`
- All paths use CMake variables for portability
- Database name and configuration file are parameterized for easy modification
- Working directory is set to project root for all commands

## Future Considerations

1. Add targets for:
   - Running tests
   - Creating database backups
   - Installing Python dependencies
   - Generating documentation
   - Deployment tasks

2. Consider adding CMake presets (CMakePresets.json) for different environments (dev, staging, production)

3. Integrate with CI/CD pipelines using CMake targets

## References

- [CMake Documentation](https://cmake.org/documentation/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
- Project CMakeLists.txt: `c:\Odoo\CMakeLists.txt`
