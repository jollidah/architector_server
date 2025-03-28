FROM messense/rust-musl-cross:x86_64-musl AS builder

WORKDIR /src
COPY . .
