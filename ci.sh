echo "Running tests..."
python3 test_imgur_migrate.py

echo "Building binary..."
pyinstaller imgur_migrate.py

echo "Installing binary..."
sh install.sh