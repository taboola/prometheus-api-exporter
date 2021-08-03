# JSON API Exporter
Prometheus JSON api exporter scrapes remote JSON from multiple targets.<br>
The exporter get as parameter a json url and convert it to a Prometheus metrics. <br>
The exporter parser support currently this two type of jsons structures. <br>

#### Supported JSON structures:
##### Type A 
```json
[
  {
    "name": "temperatures_celsius",
    "help": "temperatures in celsius",
    "labels": [
      "some_label_a",
      "some_label_b"
    ],
    "metrics": [
      {
        "labels_values": [
          "some_label_a",
          "some_label_b"
        ],
        "metric": 27
      },
      {
        "labels_values": [
          "some_label_a",
          "some_label_b"
        ],
        "metric": 24
      }
    ]
  }
]
```

#### Type B
```json
[
  {
    "name": "temperatures_celsius",
    "help": "temperatures in celsius",
    "labels": [
      "some_label_a",
      "some_label_b"
    ],
    "metrics": [
      {
        "labels_values": [
          "some_label_a",
          "some_label_b"
        ],
        "metric": 27
      },
      {
        "labels_values": [
          "some_label_a",
          "some_label_b"
        ],
        "metric": 24
      }
    ]
  },
  {
    "name": "temperature_sensor_alive",
    "help": "liveness of the sensor",
    "labels": [
      "some_label_x",
      "some_label_y"
    ],
    "value": 4
  }
]
```

### Install and Run

#### Manual Setup

```shell
# Install
$ pip install -r requirements.txt

# Run
$ python manage.py runserver 9115

# Test
$ curl http://localhost:9115/metrics?target=xx
```

### Docker
#### Build local

```shell
# Install
$ docker build . -t json-api-exporter:latest
```
#### Run

```shell
# Install
$ docker run -p 9115:9115 json-api-exporter:latest
```



## Prometheus job configuration
See also in examples/prometheus.yaml

```yaml
scrape_configs:
  - job_name: 'json-api-exporter'
    metrics_path: /probe
    static_configs:
      - targets:
        - http://target/to/json    # Target to json api
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115 
```