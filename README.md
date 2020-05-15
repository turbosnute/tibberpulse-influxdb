# tibberpulse-influxdb-rpi
Fetch Tibber Pulse data from the Tibber Pulse API web socket and place it in your influxdb.

Based on oysteoh's [tibber-pypulse-ws](https://github.com/oysteoh/tibber-pypulse-ws).

## How to build
```
docker build -t turbosnute/tibberpulse-influxdb:latest -t turbosnute/tibberpulse-influxdb:v1.0.
```

## How to run
```
docker run -d \
 -e INFLUXDB_HOST="localhost" \
 -e INFLUXDB_PORT="8086" \
 -e INFLUXDB_USER="root" \
 -e INFLUXDB_PW="root" \
 -e INFLUXDB_DATABASE="tibberPulse" \
 -e TIBBER_TOKEN="" \
 -e TIBBER_HOMEID="" \
 --name "tibberpulse-influxdb" \
turbosnute/tibberpulse-influxdb-rpi:latest
```

