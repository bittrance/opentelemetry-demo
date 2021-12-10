# opentelemetry-demo

This is a small test application that just creates tracesID.

## Docker

How to run using docker:

```shell
docker run --rm -it -p 8080:8080 -e TRACE_URL=http://grafana-agent:12345 ghcr.io/bittrance/opentelemetry-demo:main
```

## Kubernetes

To deploy the application to kubernetes you can perform the following.
This is just a simple example and not a way we recommend to deploy the application for long term usage.

The example don't use uwsgi.

```shell
kubectl run otp --image=ghcr.io/bittrance/opentelemetry-demo:main --port=8080 --env=TRACE_URL="http://grafana-agent-traces.observability.svc.cluster.local:4318/v1/traces" --env="PYTHONPATH=/venv/lib/python3.8/site-packages" --image-pull-policy=Always --command -- /usr/bin/python3.8 /work/main.py
```
