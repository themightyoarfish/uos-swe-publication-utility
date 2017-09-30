#!/usr/bin/env bash

function exit_on_fail {
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo "error with $1" >&2
        exit $status
    fi
}
echo "Compiling (1/3)..."
exit_on_fail pdflatex -interaction nonstopmode *.tex > /dev/null;
echo "Running bibtex (1/2)..."
for f in *.aux; do bibtex "$f" > /dev/null; done
echo "Running bibtex (2/2)..."
for f in *.aux; do bibtex "$f" > /dev/null; done
echo "Compiling (2/3)..."
exit_on_fail pdflatex -interaction nonstopmode *.tex > /dev/null;
echo "Compiling (3/3)..."
exit_on_fail pdflatex -interaction nonstopmode *.tex > /dev/null;
echo "Your document is now ready."
