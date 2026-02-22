FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# System dependencies for CYTools (FLINT, PPL, CGAL, GMP, MPFR, Cython build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgmp-dev \
    libmpfr-dev \
    libflint-dev \
    libppl-dev \
    libcgal-dev \
    libglpk-dev \
    m4 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies — CYTools and everything needed for the project
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
