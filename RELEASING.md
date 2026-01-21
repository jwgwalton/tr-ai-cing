# Quick Release Guide

This guide provides step-by-step instructions for publishing a new version of `tr-ai-cing` to PyPI.

## Prerequisites

Before your first release, complete the following one-time setup:

### 1. Configure Trusted Publishing on PyPI

**For Production PyPI:**
1. Log in to [PyPI](https://pypi.org/)
2. Go to your account settings
3. Navigate to "Publishing" → "Add a new publisher"
4. Fill in:
   - **PyPI Project Name**: `tr-ai-cing`
   - **Owner**: `jwgwalton`
   - **Repository**: `tr-ai-cing`
   - **Workflow name**: `publish-pypi.yml`
   - **Environment name**: Leave empty
5. Save the configuration

**For Test PyPI (optional, for testing):**
1. Log in to [Test PyPI](https://test.pypi.org/)
2. Follow the same steps as above

## Release Process

### Step 1: Prepare the Release

1. **Update version numbers** in both files:
   ```bash
   # Update version in both files to match (e.g., "0.2.0")
   vim src/tracing/__init__.py    # Update __version__
   vim pyproject.toml             # Update version
   ```

2. **Update CHANGELOG.md**:
   ```bash
   vim CHANGELOG.md
   ```
   - Move items from `[Unreleased]` to a new version section
   - Add the release date
   - Create new `[Unreleased]` section

3. **Commit version changes**:
   ```bash
   git add src/tracing/__init__.py pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push
   ```

### Step 2: Test Locally (Optional but Recommended)

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build the package
python -m build

# Check the distribution
twine check dist/* || echo "Warning: twine check may show false positives for new metadata format"

# Test installation in a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/*.whl
python -c "from tracing import Tracer, Visualizer; print('Success!')"
deactivate
rm -rf test_env
```

### Step 3: Publish to Test PyPI (Optional)

Test your release on Test PyPI first:

1. Go to your repository on GitHub
2. Click "Actions" → "Publish to PyPI"
3. Click "Run workflow"
4. Select environment: `testpypi`
5. Click "Run workflow"
6. Wait for the workflow to complete

Test the installation:
```bash
pip install --index-url https://test.pypi.org/simple/ tr-ai-cing
```

### Step 4: Create GitHub Release

This is the **recommended production release method**:

1. **Create and push a tag**:
   ```bash
   git tag v0.2.0  # Match the version number
   git push origin v0.2.0
   ```

2. **Create a GitHub Release**:
   - Go to: https://github.com/jwgwalton/tr-ai-cing/releases/new
   - Select the tag you just pushed (e.g., `v0.2.0`)
   - Release title: `v0.2.0` (or descriptive like "v0.2.0 - Feature Name")
   - Description: Copy relevant sections from CHANGELOG.md
   - Click "Publish release"

3. **Monitor the workflow**:
   - The GitHub Action will automatically trigger
   - Go to "Actions" tab to monitor progress
   - The package will be published to PyPI automatically

### Step 5: Verify the Release

1. **Wait a few minutes** for PyPI to update

2. **Test installation**:
   ```bash
   pip install --upgrade tr-ai-cing
   python -c "import tracing; print(tracing.__version__)"
   ```

3. **Check PyPI page**:
   - Visit: https://pypi.org/project/tr-ai-cing/
   - Verify the new version is listed
   - Check that the description renders correctly

## Manual Publishing (Alternative)

If the automated workflow fails or you need to publish manually:

```bash
# Install publishing tools
pip install build twine

# Build
python -m build

# Upload to Test PyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

You'll need to configure PyPI API tokens in your environment if not using trusted publishing.

## Troubleshooting

### Workflow Fails with 403 Error

- Check that trusted publishing is configured correctly
- Verify the repository name and workflow name match exactly

### Package Already Exists

- You cannot re-upload the same version
- Bump the version number and try again

### Import Fails After Installation

- Check that both version numbers were updated
- Verify the package structure hasn't changed
- Test locally before publishing

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backwards compatible)
- **PATCH** (0.0.X): Bug fixes (backwards compatible)

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.1.0` → `1.0.0`: First stable release with breaking changes

## Post-Release Checklist

- [ ] Verify package appears on PyPI
- [ ] Test installation: `pip install tr-ai-cing`
- [ ] Verify version: `python -c "import tracing; print(tracing.__version__)"`
- [ ] Check PyPI page renders correctly
- [ ] Update any deployment documentation if needed
- [ ] Announce the release (Twitter, blog, etc.) if desired

## Need Help?

- Review [PUBLISHING.md](./PUBLISHING.md) for detailed documentation
- Check GitHub Actions logs for error messages
- Consult [PyPI Help](https://pypi.org/help/)
