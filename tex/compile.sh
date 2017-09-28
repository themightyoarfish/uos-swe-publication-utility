#!/usr/bin/env bash

echo "Compiling (1/3)..."
pdflatex *.tex > /dev/null;
echo "Running bibtex (1/2)..."
for f in *.aux; do bibtex "$f" > /dev/null; done
echo "Running bibtex (2/2)..."
for f in *.aux; do bibtex "$f" > /dev/null; done
echo "Compiling (2/3)..."
pdflatex *.tex > /dev/null;
echo "Compiling (3/3)..."
pdflatex *.tex > /dev/null;
echo "Your document is now ready."
