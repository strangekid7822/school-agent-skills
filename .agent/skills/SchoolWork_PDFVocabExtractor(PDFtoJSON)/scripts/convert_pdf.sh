#!/bin/bash
# PDF to PNG converter for vocabulary extraction
# Usage: ./convert_pdf.sh <input_pdf> [output_dir] [dpi]

set -e

INPUT_PDF="$1"
OUTPUT_DIR="${2:-.agent/workspace/pdf_extractor/output}"
DPI="${3:-200}"

if [ -z "$INPUT_PDF" ]; then
    echo "Usage: $0 <input_pdf> [output_dir] [dpi]"
    echo "  input_pdf  - Path to PDF file"
    echo "  output_dir - Output directory (default: .agent/workspace/pdf_extractor/output)"
    echo "  dpi        - Resolution (default: 200)"
    exit 1
fi

if [ ! -f "$INPUT_PDF" ]; then
    echo "Error: File not found: $INPUT_PDF"
    exit 1
fi

# Check for pdftoppm
if ! command -v pdftoppm &> /dev/null; then
    echo "Error: pdftoppm not found. Install with: brew install poppler"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get base filename without extension
BASENAME=$(basename "$INPUT_PDF" .pdf)

# Convert PDF to PNG
echo "Converting: $INPUT_PDF"
echo "Output: $OUTPUT_DIR"
echo "DPI: $DPI"

pdftoppm -png -r "$DPI" "$INPUT_PDF" "$OUTPUT_DIR/$BASENAME"

echo "Done! Generated files:"
ls -la "$OUTPUT_DIR"/*.png 2>/dev/null || echo "No PNG files found"
