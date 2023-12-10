# Build the Docker image
`docker build --tag lordb .`

# Run a script
`docker run --rm --mount type=bind,source=$(pwd),target=/root/lordb lordb python3 lor_keywords.py`

