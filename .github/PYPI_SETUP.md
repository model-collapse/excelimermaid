# PyPI Publishing Setup

This repository uses GitHub Actions with PyPI Trusted Publishing for automated package releases.

## Initial Setup (One-time)

### 1. Configure PyPI Trusted Publishing

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name**: `excelimermaid`
   - **Owner**: `model-collapse`
   - **Repository name**: `excelimermaid`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

### 2. Create GitHub Environment (Optional but recommended)

1. Go to repository Settings → Environments
2. Create environment named `pypi`
3. Add protection rules:
   - Required reviewers (optional)
   - Deployment branches: Only selected branches → main

## Publishing a Release

### Method 1: GitHub Release (Recommended)

1. Create a new tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

2. Go to GitHub → Releases → "Create a new release"
3. Choose the tag (v0.1.0)
4. Add release notes
5. Click "Publish release"

The workflow will automatically:
- Build the package
- Publish to PyPI
- Available at: https://pypi.org/project/excelimermaid/

### Method 2: Manual Trigger

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. This will publish to TestPyPI for testing

## Version Updates

Before creating a release, update the version in:
- `setup.py` (line 12: `version="0.1.0"`)

## Testing Before Publishing

Test on TestPyPI first:
1. Manually trigger the workflow (Method 2 above)
2. Install from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ excelimermaid
   ```

## Troubleshooting

**Error: "Trusted publishing exchange failure"**
- Ensure PyPI trusted publisher is configured correctly
- Check that environment name matches exactly: `pypi`
- Verify workflow file name is `publish.yml`

**Error: "Project already exists"**
- For first release, you may need to register the project name on PyPI first
- Or use manual upload with API token for the first version

## Alternative: Using API Token

If trusted publishing doesn't work initially:

1. Create API token at https://pypi.org/manage/account/token/
2. Add to GitHub Secrets as `PYPI_API_TOKEN`
3. Modify workflow to use token authentication

## References

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions PyPI Publish](https://github.com/marketplace/actions/pypi-publish)
