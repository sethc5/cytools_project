FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# System dependencies for CYTools (FLINT, PPL, CGAL, GMP, MPFR, Cython build)
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    m4 \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    libflint-dev \
    libppl-dev \
    libcgal-dev \
    libglpk-dev \
    autoconf \
    libtool \
    && rm -rf /var/lib/apt/lists/*

# Build deps first (Cython needed before pplpy/cysignals can compile)
RUN pip install --no-cache-dir \
    Cython \
    setuptools \
    wheel \
    packaging \
    numpy

# Install cysignals and gmpy2 first (pplpy depends on them)
RUN pip install --no-cache-dir cysignals gmpy2

# Install pplpy (needs cysignals + libppl headers)
RUN pip install --no-cache-dir pplpy

# Install python-flint (needs libflint headers)
RUN pip install --no-cache-dir python-flint

# Install remaining CYTools dependencies and CYTools itself
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
