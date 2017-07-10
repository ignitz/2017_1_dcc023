for x in $(ps aux | grep '[p]ython3 serventTP3.py' | awk '{print $2}'); do
  kill -9 $x
done
