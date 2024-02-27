# Build and run the container
# --rm means don't store changes
docker build -t orcidscraper . && docker run --rm -p 5001:5001 orcidscraper