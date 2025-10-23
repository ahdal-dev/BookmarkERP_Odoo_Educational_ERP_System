# ADR 001: Add Makefile for Odoo Project Task Management

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

We will adopt **GNU Make** (Makefile) as a task runner for the Odoo project to provide simple, standardized commands for common development tasks.

### Implementation Details

A `Makefile` has been created at the project root with the following targets:

1. **`config`** - Configure database and update base module
   ```bash
   python odoo/odoo-bin -c odoo.conf -d edu_demo_new -u base --stop-after-init
   ```

2. **`run`** - Start Odoo server manually
   ```bash
   python odoo/odoo-bin -c odoo.conf
   ```

3. **`install`** - Install Python dependencies
   ```bash
   pip install -r odoo/requirements.txt
   ```

4. **`update-module`** - Update specific custom modules

5. **`clean`** - Clean Python cache files

### Usage

```bash
# Run targets directly
make config
make run
make install
make update-module MODULE=education_management
```

## Rationale

### Why Makefile?

1. **Simplicity** - Straightforward syntax, easy to read and maintain
2. **Standard tool** - Make is the de facto standard for task runners
3. **No configuration step** - Just run `make <target>` directly
4. **Lightweight** - No build directories or complex setup
5. **Python-friendly** - More idiomatic for Python projects than CMake
6. **Documentation as code** - Commands are self-documenting in the Makefile
7. **Extensibility** - Easy to add new targets for testing, deployment, etc.

### Alternatives Considered

1. **CMake**
   - ❌ Overkill for a Python project (designed for C/C++)
   - ❌ Requires configuration step (`cmake -B build`)
   - ❌ More complex syntax and setup
   - ❌ Compiler detection issues on Windows
   - ✅ Strong IDE integration

2. **Shell scripts (bash/PowerShell)**
   - ❌ Platform-specific (need separate scripts for Windows/Unix)
   - ❌ No standardized interface
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
- **Self-documenting** - `make help` shows available targets
- **Simple syntax** - Easy to read and modify
- **No setup required** - Just run `make <target>` directly
- **Reduced errors** - Centralized command definitions prevent typos
- **Easy onboarding** - New developers can see available commands with `make help`
- **Extensible** - Easy to add new targets for CI/CD, testing, deployment
- **Standard tool** - Make is widely known and available

### Negative

- **Windows compatibility** - Requires GNU Make or nmake (not built-in)
- **Limited IDE integration** - Less support than CMake in some IDEs
- **Syntax quirks** - Tab vs space requirements can be confusing

### Neutral

- **Maintenance** - Makefile needs updates when adding new common tasks
- **Platform differences** - Some commands may need adjustment for Linux/macOS

## Implementation Notes

- Python executable uses virtual environment path (`venv/Scripts/python.exe`)
- All paths are defined as variables at the top of the Makefile
- Database name and configuration file are parameterized for easy modification
- `.PHONY` targets ensure commands run even if files with those names exist
- Help target provides self-documentation

## Future Considerations

1. Add targets for:
   - Running tests
   - Creating database backups
   - Generating documentation
   - Deployment tasks
   - Database migrations

2. Create environment-specific targets (dev, staging, production)

3. Integrate with CI/CD pipelines using Make targets

4. Add Linux/macOS compatibility adjustments if needed

## References

- [GNU Make Documentation](https://www.gnu.org/software/make/manual/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
- Project Makefile: `c:\Odoo\Makefile`
