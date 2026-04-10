FROM gcc:14
RUN apt-get update && apt-get install -y --no-install-recommends cmake \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN mkdir -p build/Release \
    && cmake -DCMAKE_BUILD_TYPE=Release -S . -B build/Release \
    && cmake --build build/Release
ENTRYPOINT ["./build/Release/output_id"]
