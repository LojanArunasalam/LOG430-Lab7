for i in {1..10}; do
  echo "Request $i:"
  curl -s -I http://localhost:8002/warehouse/ | grep "X-Instance-ID"
  echo "---"
done