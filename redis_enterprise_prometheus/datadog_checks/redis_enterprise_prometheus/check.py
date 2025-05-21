from typing import Any  # noqa: F401

from datadog_checks.base import AgentCheck, ConfigurationError, OpenMetricsBaseCheckV2

from .metrics import ADDITIONAL_METRICS, COUNTER_METRICS, DEFAULT_METRICS


class RedisEnterprisePrometheusCheck(OpenMetricsBaseCheckV2):

    # This will be the prefix of every metric and service check the integration sends
    __NAMESPACE__ = 'rdse2'

    def __init__(self, name, init_config, instances):

        super(RedisEnterprisePrometheusCheck, self).__init__(name, init_config, instances)
        self.instance.setdefault("tls_verify", False)
        self.check_initializations.appendleft(self._parse_config)

    def _parse_config(self):
        self.scraper_configs = []
        metrics_endpoint = self.instance.get('openmetrics_endpoint')
        metrics = self.get_default_config()
        # Explicitly override all counter metrics to be gauges
        for metric_group in metrics:
            for metric_name in list(metric_group.keys()):
                # Check if this metric is in the COUNTER_METRICS list
                if metric_name in COUNTER_METRICS:
                    val = metric_group[metric_name]

                    if isinstance(val, str):
                        # First time: wrap as dict and set type
                        metric_group[metric_name] = {
                            'name': val,
                            'type': 'gauge',
                        }
                    elif isinstance(val, dict):
                        # Already wrapped: just override type
                        val['type'] = 'gauge'
                    else:
                        raise TypeError(f"Unexpected type for {metric_name}: {type(val)} — {val}")


        additional = []
        groups = self.instance.get('extra_metrics', [])
        for g in groups:
            if g not in ADDITIONAL_METRICS.keys():
                raise ConfigurationError(f'invalid group in extra_metrics: {g}')
            additional.append(ADDITIONAL_METRICS[g])

        if len(additional) > 0:
            # Also apply gauge type to any counter metrics in additional metric groups
            for metric_group in additional:
                for metric_name in list(metric_group.keys()):
                    if metric_name in COUNTER_METRICS:
                        val = metric_group[metric_name]
                        
                        if isinstance(val, str):
                            # First time: wrap as dict and set type
                            metric_group[metric_name] = {
                                'name': val,
                                'type': 'gauge',
                            }
                        elif isinstance(val, dict):
                            # Already wrapped: just override type
                            val['type'] = 'gauge'
                        else:
                            raise TypeError(f"Unexpected type for {metric_name}: {type(val)} — {val}")
                            
            self.service_check("more_groups", AgentCheck.OK)
            metrics += additional

        excludes = self.instance.get('exclude_metrics', [])
        for m in excludes:
            found = False
            for mg in metrics:
                if m in mg.keys():
                    mg.pop(m)
                    found = True
            if not found:
                raise ConfigurationError(f'invalid metric in excludes: {m}')

        config = {
            'openmetrics_endpoint': metrics_endpoint,
            'namespace': self.__NAMESPACE__,
            'metrics': metrics,
            'metadata_label_map': {'version': 'version'},
        }

        config.update(self.instance)
        self.scraper_configs.append(config)

    def get_default_config(self):

        metrics = []
        for dm in DEFAULT_METRICS:
            metrics.append(dm)
        return metrics

    def can_connect(self, hostname=None, message=None, tags=None):
        print(f'hostname: {hostname}, message: {message}, tags: {tags}')
        return False
