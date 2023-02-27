# tibberpulse-influxdb
Fetch Tibber Pulse data from the Tibber Pulse API web socket and place it in your influxdb.

## Create Influxdb database

### Run InfluxDB in Docker
If you don't have a Influxdb server yet you can run one in Docker:
```
$ docker run -d -p 8086:8086 \
      -v influxdb:/var/lib/influxdb \
      influxdb
```

### Create Dabatase
```
$ curl -G http://<INFLUXDB_SERVER:8086/query --data-urlencode "q=CREATE DATABASE tibberPulse"
```

## How to obtain Tibber Token
### Tibber Token
- Go to https://developer.tibber.com/ and Sign in.
- Genrerate a new token.

## How to run
```
docker run -d \
 -e INFLUXDB_HOST="influx ip or hostname" \
 -e INFLUXDB_PORT="8086" \
 -e INFLUXDB_USER="root" \
 -e INFLUXDB_PW="root" \
 -e INFLUXDB_DATABASE="tibberPulse" \
 -e TIBBER_TOKEN="" \
 --name "tibberpulse-influxdb" \
turbosnute/tibberpulse-influxdb-rpi:latest
```

## Common Issues
### Too many open connections on this server: 2;
The quickest way to fix the "Too many open connections on this server" issue is just to generate a new Tibber Access Token and start the container again (remember to set the new token in the TIBBER_TOKEN variable).

## Advanced Options

### Specify homeID
By default this container will fetch the first home id from Tibber and use it. If you want to specify the home id you first have to find it.
- Go to https://developer.tibber.com/explorer
- Make sure you are signed in.
- Click "Load Personal Token"
- From the dropdown to the right choose "Real time subscriptions"
- You can now see your homeId in the GraphiQL code.
![tibber printscreen](https://github.com/turbosnute/tibberpulse-influxdb/raw/master/tibberSnapshot.png "tibber printscreen")

Then you can use the env variable TIBBER_HOMEID when you run the container:
```
-e TIBBER_HOMEID="aaaaaaaaaaa-aaaa-aaaa-aaaaaaaaaa" \
```
