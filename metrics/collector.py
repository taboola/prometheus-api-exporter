from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily

from api_exporter.http import HttpManager


class GenericApiCollector(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def collect(self, data={}):
        try:
            resp = (HttpManager().query(data['endpoint']))
            if resp:
                counter = self.parse_data(resp)
                for c in counter:
                    yield c
            else:
                yield GaugeMetricFamily('generic_api_exporter', 'empty', value=0)
        except Exception as e:
            yield GaugeMetricFamily('generic_api_exporter', 'empty', value=0)

    def parse_data(self, data):
        resp = []
        for d in data:
            if not d.get('value', None):
                c = CounterMetricFamily(d['name'], d['help'], labels=d['labels'])
                try:
                    for metric in d['metrics']:
                        if metric['metric']:
                            c.add_metric(metric['labels_values'], metric['metric'])
                except Exception as e:
                    pass
            else:
                c = CounterMetricFamily(d['name'], d['help'], value=d['value'])
            resp.append(c)
        return resp
