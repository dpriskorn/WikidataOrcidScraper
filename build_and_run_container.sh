# Build and run the container
# --rm means don't store changes
docker build -t orcidscraper . && docker run --rm -p 6000:6000 orcidscraper