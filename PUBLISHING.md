# Publishing to PyPI

This document describes how to publish the `tr-ai-cing` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both [Test PyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **GitHub Trusted Publisher**: Configure trusted publishing in PyPI (recommended) or create API tokens

## Automated Publishing (Recommended)

### Option 1: Publish via GitHub Release

This is the recommended approach for production releases.

1. Update the version in `src/tracing/__init__.py` and `pyproject.toml`
2. Commit and push your changes
3. Create a new release on GitHub:
   - Go to the repository on GitHub
   - Click "Releases" → "Create a new release"
   - Choose a tag (e.g., `v0.1.0`)
   - Fill in release notes
   - Click "Publish release"
4. The GitHub Action will automatically build and publish to PyPI

### Option 2: Manual Trigger via GitHub Actions

For testing or manual deployments:

1. Go to the repository on GitHub
2. Click "Actions" → "Publish to PyPI"
3. Click "Run workflow"
4. Select the environment:
   - `testpypi` - Publish to Test PyPI for testing
   - `pypi` - Publish to production PyPI
5. Click "Run workflow"

## Setting Up Trusted Publishing

Trusted publishing eliminates the need for API tokens by using OpenID Connect (OIDC).

### For PyPI

1. Log in to [PyPI](https://pypi.org/)
2. Go to your account settings
3. Navigate to "Publishing" → "Add a new publisher"
4. Fill in the details:
   - **PyPI Project Name**: `tr-ai-cing`
   - **Owner**: `jwgwalton`
   - **Repository**: `tr-ai-cing`
   - **Workflow name**: `publish-pypi.yml`
   - **Environment name**: Leave empty (or specify if using environments)
5. Save the configuration

### For Test PyPI

1. Log in to [Test PyPI](https://test.pypi.org/)
2. Follow the same steps as above
3. Project name: `tr-ai-cing`

## Manual Publishing (Alternative)

If you need to publish manually from your local machine:

### Install Build Tools

```bash
pip install build twine
```

### Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates two files in the `dist/` directory:
- A source distribution (`.tar.gz`)
- A wheel distribution (`.whl`)

### Check the Build

```bash
twine check dist/*
```

### Upload to Test PyPI (for testing)

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for your Test PyPI credentials.

Test the installation:
```bash
pip install --index-url https://test.pypi.org/simple/ tr-ai-cing
```

### Upload to PyPI (production)

```bash
twine upload dist/*
```

You'll be prompted for your PyPI credentials.

## Version Management

The version is defined in two places and must be kept in sync:

1. `pyproject.toml` - Line 7: `version = "0.1.0"`
2. `src/tracing/__init__.py` - Line 7: `__version__ = "0.1.0"`

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality (backwards compatible)
- **PATCH** version (0.0.X): Bug fixes (backwards compatible)

### Version Bump Checklist

Before releasing a new version:

1. [ ] Update `__version__` in `src/tracing/__init__.py`
2. [ ] Update `version` in `pyproject.toml`
3. [ ] Update CHANGELOG.md (if you have one)
4. [ ] Run tests: `pytest`
5. [ ] Build and test locally: `python -m build && pip install dist/*.whl`
6. [ ] Commit version changes: `git commit -m "Bump version to X.Y.Z"`
7. [ ] Tag the commit: `git tag vX.Y.Z`
8. [ ] Push with tags: `git push && git push --tags`
9. [ ] Create GitHub release or trigger workflow

## API Tokens (Alternative to Trusted Publishing)

If you prefer using API tokens instead of trusted publishing:

### Create API Token

1. Log in to PyPI/Test PyPI
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Name: `tr-ai-cing-github-actions`
5. Scope: Project (`tr-ai-cing`)
6. Copy the token (starts with `pypi-`)

### Add to GitHub Secrets

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN` (for PyPI) or `TEST_PYPI_API_TOKEN` (for Test PyPI)
5. Value: Paste the token
6. Click "Add secret"

### Update Workflow

Modify `.github/workflows/publish-pypi.yml` to use tokens instead of trusted publishing:

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## Troubleshooting

### Build Fails

- Ensure all dependencies are listed in `pyproject.toml`
- Check that `src/tracing/__init__.py` exports all public APIs
- Verify MANIFEST.in includes all necessary files

### Upload Fails

- **403 Forbidden**: Check API token or trusted publisher configuration
- **400 Bad Request**: Package name or version might already exist
- **File already exists**: Cannot re-upload same version; bump version number

### Import Fails After Installation

- Ensure package structure follows Python conventions
- Check that `__init__.py` files exist in all package directories
- Verify `pyproject.toml` has correct `where` setting in `[tool.setuptools.packages.find]`

## Testing the Package

After publishing to Test PyPI:

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ tr-ai-cing

# Test import and basic functionality
python -c "from tracing import Tracer, Visualizer; print('Success!')"

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

## Useful Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging User Guide](https://packaging.python.org/)
