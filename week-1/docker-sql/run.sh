echo "Building image ..."
docker build -t test:pandas .
echo "Successfully built image  ..."

echo "Starting image ..."
docker run -it test:pandas