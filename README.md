CodeScope 360

ctrlAltMind Edition — Python Project Structure Scanner

CodeScope 360 is a simple, no-frills Python script that scans the structure of a Python project and generates a detailed Markdown report.
It's not polished. But it works (most of the time).

It was built to save time when trying to understand unfamiliar codebases — by summarizing their structure, key files, and relationships.

Features

Recursive directory scan

Detects main entry points (if __name__ == "__main__")

Extracts classes, functions, comments, and docstrings

Maps internal and external imports

Reads requirements.txt and loosely categorizes dependencies

Generates a clean, structured Markdown report

How to Use

python codescope360.py [project_path] 

If no path is provided, it scans the current directory.

The result is a Markdown file named like:

codescope_[project-name]_[timestamp].md 

Requirements

Python 3.x

No external libraries needed

Warnings

The analysis is static and based on patterns — false positives or missed elements are possible.

It’s lightly tested. Use common sense and feel free to improve it.

Why

I made this for myself. If it helps you too, great. If not, that’s fine.
You’re free to fork, tweak, or throw it away.

ctrlAltMind — organized chaos, occasional code

License

MIT License

Copyright (c) 2025 ctrlAltMind

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

