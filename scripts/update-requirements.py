#!/usr/bin/env python3
import subprocess

subprocess.run([
    "pip-compile", "requirements.in", "--output-file", "requirements.txt"
], check=True)