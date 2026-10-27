# kafka-namer

Tiny CLI that generates two-word names (e.g. `swift-otter`) for Kafka clusters.

## Usage

```bash
pip install -e ".[dev]"

kafka-namer                      # swift-otter
kafka-namer -n 3 --prefix prod   # three unique names, prefixed with "prod-"
kafka-namer --seed 42            # reproducible output
```

## Tests

```bash
pytest
```
