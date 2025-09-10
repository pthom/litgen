#!/bin/bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

REPO_DIR=$SCRIPT_DIR/..

cd $SCRIPT_DIR
rm -rf _build
rm -rf $REPO_DIR/docs/litgen_book
jupyter-book build .
cp -a _build/html $REPO_DIR/docs/litgen_book

# Build PDF version (uncomment if needed)
jupyter-book build . --builder pdfhtml
cp _build/pdf/book.pdf $REPO_DIR/docs/litgen_book/litgen_book.pdf
