#!/bin/bash
find . -name "*.fz" -type f -exec ./funpack -C {} \;
