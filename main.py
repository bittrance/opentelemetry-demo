from argparse import ArgumentParser
import os
from bottle import Bottle, HTTPResponse, request, response, static_file
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

parser = ArgumentParser()
parser.add_argument("--trace-url", default=os.environ.get("TRACE_URL", None))

tracer = None


def configure(args):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: "opentelemetry-demo"}))
    )
    exporter = OTLPSpanExporter(
        endpoint=args.trace_url,
        # credentials=ChannelCredentials(credentials),
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    global tracer
    tracer = trace.get_tracer(__name__)


app = Bottle()


@app.get("/")
def retrieve():
    with tracer.start_as_current_span("retrieve"):
        return {"hello": "world"}


CONFIGURED = False


def uwsgi_entrypoint(environ, start_response):
    global CONFIGURED
    if not CONFIGURED:
        args = parser.parse_args()
        configure(args)
        CONFIGURED = True
    try:
        return app(environ, start_response)
    except Exception as err:
        print(err)
        raise err


if __name__ == "__main__":
    parser.add_argument("--bottle-host", default="0.0.0.0")
    parser.add_argument("--bottle-port", default=8080)
    args = parser.parse_args()
    configure(args)
    with tracer.start_as_current_span("starting"):
        app.run(
            host=args.bottle_host, reloader=False, port=args.bottle_port, debug=True
        )
