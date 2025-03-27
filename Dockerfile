FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

COPY justfile .

# create ~/bin
RUN mkdir -p /root/bin

# download and extract just to ~/bin/just
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /root/bin

# add `/root/bin` to the paths that your shell searches for executables
ENV PATH="/root/bin:${PATH}"

# just should now be executable
RUN just --help

EXPOSE 8000
