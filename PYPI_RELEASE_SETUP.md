# PyPI Release Setup Guide

This document explains how to set up PyPI trusted publishing and create releases for the `metaclass-registry` package.

## Prerequisites

- Repository owner or admin access to configure PyPI trusted publishing
- Access to the PyPI account that owns or will own the `metaclass-registry` package

## Step 1: Configure PyPI Trusted Publishing

Trusted publishing allows GitHub Actions to publish to PyPI without manually managing API tokens. This is the recommended and most secure method.

### 1.1 Create the PyPI Project (if not already created)

1. Go to [PyPI](https://pypi.org/) and log in
2. If this is the first release, you'll configure the publisher BEFORE uploading
3. Go to your account settings: https://pypi.org/manage/account/publishing/

### 1.2 Add GitHub as a Trusted Publisher

1. Navigate to: https://pypi.org/manage/account/publishing/
2. Scroll to the "Add a new pending publisher" section
3. Fill in the following information:
   - **PyPI Project Name**: `metaclass-registry`
   - **Owner**: `trissim`
   - **Repository name**: `metaclass-registry`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

**Important**: The environment name `pypi` must match the environment specified in the GitHub Actions workflow.

## Step 2: Create GitHub Environment (Optional but Recommended)

Creating a GitHub environment adds an extra layer of protection by allowing you to:
- Require manual approval before publishing
- Restrict which branches can trigger publishing
- Add environment-specific secrets

### 2.1 Create the Environment

1. Go to your repository settings: https://github.com/trissim/metaclass-registry/settings/environments
2. Click "New environment"
3. Name it: `pypi`
4. Configure protection rules (optional):
   - **Required reviewers**: Add yourself or team members to require approval
   - **Deployment branches**: Set to "Protected branches only" or specific branches

## Step 3: Create and Push a Release Tag

The GitHub Actions workflow is configured to trigger on tags starting with `v`:

```bash
# Ensure you're on the main branch and up to date
git checkout main
git pull origin main

# Create and push a tag for version 0.1.0
git tag v0.1.0
git push origin v0.1.0
```

## Step 4: Monitor the Release

1. Go to the Actions tab: https://github.com/trissim/metaclass-registry/actions
2. Watch the "Publish to PyPI" workflow run
3. Once complete, verify the package on PyPI: https://pypi.org/project/metaclass-registry/

## Workflow Overview

The publish workflow (`.github/workflows/publish.yml`) performs these steps:

1. **Checkout code**: Gets the tagged version
2. **Set up Python**: Installs Python 3.12
3. **Install build dependencies**: Installs the `build` package
4. **Build package**: Creates wheel and source distributions
5. **Check distribution**: Validates the package with twine
6. **Create GitHub Release**: Creates a GitHub release with auto-generated notes
7. **Publish to PyPI**: Uploads to PyPI using trusted publishing (no tokens needed!)

## Version Bumping for Future Releases

For subsequent releases, update the version in two places:

1. **pyproject.toml**: Update the `version` field:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. **src/metaclass_registry/__init__.py**: Update the `__version__` variable:
   ```python
   __version__ = "0.2.0"
   ```

Then create and push a new tag:
```bash
git tag v0.2.0
git push origin v0.2.0
```

## Testing the Build Locally

Before creating a release tag, you can test the build process locally:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the distribution (note: may show warnings, but PyPI will accept it)
twine check dist/*

# Clean up
rm -rf dist/
```

## Troubleshooting

### "Invalid credentials" error
- Ensure PyPI trusted publishing is configured correctly
- Verify the workflow name and environment name match exactly
- Check that the repository owner and name are correct

### Workflow doesn't trigger
- Ensure the tag starts with 'v' (e.g., `v0.1.0`, not `0.1.0`)
- Check that the workflow file is on the main/master branch

### Environment protection rules
- If you set up required reviewers, you'll need to manually approve the deployment
- Check the Actions tab for pending approvals

### "Package already exists" error
- You cannot re-upload the same version to PyPI
- Increment the version number and create a new tag
- PyPI versions are immutable once published

## Security Notes

- **Never** commit PyPI API tokens to the repository
- Trusted publishing eliminates the need for long-lived tokens
- The `id-token: write` permission is required for OIDC authentication
- Consider enabling 2FA on your PyPI account

## Additional Resources

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions: Publishing Python Packages](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
