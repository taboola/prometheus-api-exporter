from __future__ import unicode_literals

import copy
from threading import Lock

from prometheus_client.core import REGISTRY
from prometheus_client.registry import CollectorRegistry
from prometheus_client.utils import floatToGoString

try:
    from urllib import quote_plus
    from BaseHTTPServer import BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn
    from urllib2 import (
        build_opener, HTTPError, HTTPHandler, HTTPRedirectHandler, Request,
    )
    from urlparse import parse_qs, urlparse
except ImportError:
    from http.server import BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn
    from urllib.error import HTTPError
    from urllib.parse import parse_qs, quote_plus, urlparse
    from urllib.request import (
        build_opener, HTTPHandler, HTTPRedirectHandler, Request,
    )


def generate_latest(registry=REGISTRY, **kwargs):
    """Returns the metrics from the registry in latest text format as a string."""

    def sample_line(line):
        if line.labels:
            labelstr = '{{{0}}}'.format(','.join(
                ['{0}="{1}"'.format(
                    k, v.replace('\\', r'\\').replace('\n', r'\n').replace('"', r'\"'))
                    for k, v in sorted(line.labels.items())]))
        else:
            labelstr = ''
        timestamp = ''
        if line.timestamp is not None:
            # Convert to milliseconds.
            timestamp = ' {0:d}'.format(int(float(line.timestamp) * 1000))
        return '{0}{1} {2}{3}\n'.format(
            line.name, labelstr, floatToGoString(line.value), timestamp)

    output = []
    for metric in registry.collect(data=kwargs):
        try:
            mname = metric.name
            mtype = metric.type
            # Munging from OpenMetrics into Prometheus format.
            if mtype == 'counter':
                mname = mname + '_total'
            elif mtype == 'info':
                mname = mname + '_info'
                mtype = 'gauge'
            elif mtype == 'stateset':
                mtype = 'gauge'
            elif mtype == 'gaugehistogram':
                # A gauge histogram is really a gauge,
                # but this captures the structure better.
                mtype = 'histogram'
            elif mtype == 'unknown':
                mtype = 'untyped'

            output.append('# HELP {0} {1}\n'.format(
                mname, metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0} {1}\n'.format(mname, mtype))

            om_samples = {}
            for s in metric.samples:
                for suffix in ['_created', '_gsum', '_gcount']:
                    if s.name == metric.name + suffix:
                        # OpenMetrics specific sample, put in a gauge at the end.
                        om_samples.setdefault(suffix, []).append(sample_line(s))
                        break
                else:
                    output.append(sample_line(s))
        except Exception as exception:
            exception.args = (exception.args or ('',)) + (metric,)
            raise

        for suffix, lines in sorted(om_samples.items()):
            output.append('# HELP {0}{1} {2}\n'.format(metric.name, suffix,
                                                       metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0}{1} gauge\n'.format(metric.name, suffix))
            output.extend(lines)
    return ''.join(output).encode('utf-8')


class CustomCollectorRegistry(CollectorRegistry):
    """Metric collector registry.

    Collectors must have a no-argument method 'collect' that returns a list of
    Metric objects. The returned metrics should be consistent with the Prometheus
    exposition formats.
    """

    def __init__(self, auto_describe=False, target_info=None):
        self._collector_to_names = {}
        self._names_to_collectors = {}
        self._auto_describe = auto_describe
        self._lock = Lock()
        self._target_info = {}
        self.set_target_info(target_info)

    def register(self, collector):
        print('CollectorRegistry: register')
        """Add a collector to the registry."""
        with self._lock:
            names = self._get_names(collector)
            duplicates = set(self._names_to_collectors).intersection(names)
            if duplicates:
                raise ValueError(
                    'Duplicated timeseries in CollectorRegistry: {0}'.format(
                        duplicates))
            for name in names:
                self._names_to_collectors[name] = collector
            self._collector_to_names[collector] = names

    def collect(self, data={}):
        """Yields metrics from the collectors in the registry."""
        collectors = None
        ti = None
        with self._lock:
            collectors = copy.copy(self._collector_to_names)
            if self._target_info:
                ti = self._target_info_metric()
        if ti:
            yield ti
        for collector in collectors:
            for metric in collector.collect(data):
                yield metric


REGISTRY = CustomCollectorRegistry(auto_describe=True)
