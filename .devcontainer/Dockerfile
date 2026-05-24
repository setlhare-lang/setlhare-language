FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# System tools + LLVM 18 + Binaryen + WABT
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        lsb-release \
        software-properties-common \
        wget \
        gnupg \
        binaryen \
        wabt \
    && rm -rf /var/lib/apt/lists/*

# LLVM 18 toolchain
RUN wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/apt.llvm.org.gpg \
    && echo "deb http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm-18 main" > /etc/apt/sources.list.d/llvm.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        llvm-18 \
        llvm-18-dev \
        llvm-18-tools \
        clang-18 \
        lld-18 \
    && rm -rf /var/lib/apt/lists/* \
    && for tool in llc opt llvm-as llvm-dis llvm-link clang clang++ lld; do \
         update-alternatives --install /usr/bin/$tool $tool /usr/bin/$tool-18 100 || true; \
       done

# Python tooling (extras installed via postCreate)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

USER vscode
