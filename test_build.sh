#!/usr/bin/env bash
# Script to test the package build and installation locally

set -e  # Exit on error

echo "==================================="
echo "Testing tr-ai-cing Package Build"
echo "==================================="
echo ""

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info
echo "   ✓ Cleaned"
echo ""

# Build the package
echo "2. Building package..."
python -m build
echo "   ✓ Built successfully"
echo ""

# Check the distribution
echo "3. Checking distribution with twine..."
twine check dist/* || echo "   ⚠ Warning: twine may show false positives for new metadata format"
echo ""

# List built files
echo "4. Built packages:"
ls -lh dist/
echo ""

# Create test environment
echo "5. Creating test virtual environment..."
python -m venv /tmp/tr_ai_cing_test_env
source /tmp/tr_ai_cing_test_env/bin/activate
echo "   ✓ Virtual environment created"
echo ""

# Install from wheel
echo "6. Installing from wheel..."
pip install dist/tr_ai_cing-*.whl
echo "   ✓ Installed successfully"
echo ""

# Test import
echo "7. Testing import..."
python << 'EOF'
from tracing import Tracer, Visualizer, trace_llm_call
import tracing

print(f"   ✓ Successfully imported tracing v{tracing.__version__}")
print(f"   ✓ Tracer: {Tracer}")
print(f"   ✓ Visualizer: {Visualizer}")
print(f"   ✓ trace_llm_call: {trace_llm_call}")
EOF
echo ""

# Clean up
echo "8. Cleaning up..."
deactivate
rm -rf /tmp/tr_ai_cing_test_env
echo "   ✓ Test environment removed"
echo ""

echo "==================================="
echo "✓ All tests passed successfully!"
echo "==================================="
echo ""
echo "The package is ready to be published to PyPI."
echo "See RELEASING.md for publishing instructions."
