from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from conversational_agent.core.config import Settings

def confgiure_tracing(settings: Settings) -> None:
    if not settings.otel_enabled:
        return
    
    resource = Resource(attributes = {SERVICE_NAME: settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    if settings.otel_exporter_otlp_endpoint:
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
    else:
        processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    tracer.set_tracer_provider(provider)

def instrument_fastapi(app) -> None:
    FASTAPIInstrumentor.instrument_app(app)            