#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).with_name('check_agent_usage.py')
spec = importlib.util.spec_from_file_location('usage', PATH)
usage = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(usage)


class UsageParserTests(unittest.TestCase):
    def test_codex_multilimit(self):
        payload = {
            'result': {'rateLimits': {'rateLimitsByLimitId': {'codex': {
                'primary': {'usedPercent': 30, 'windowDurationMins': 300, 'resetsAt': 2000000000},
                'secondary': {'usedPercent': 12, 'windowDurationMins': 10080, 'resetsAt': 2000100000},
            }}}}
        }
        buckets = usage.parse_codex_response(payload)
        result = usage.summarize('codex', buckets, 'test', 'fixture')
        self.assertEqual(result['five_hour_remaining_percent'], 70)
        self.assertEqual(result['weekly_remaining_percent'], 88)

    def test_omp_usage_report(self):
        payload = {'reports': [{'provider': 'openai-codex', 'limits': [
            {'id': 'five-hour', 'name': '5 hour', 'amount': {'usedFraction': 0.25}, 'window': {'durationMs': 300*60*1000, 'resetsAt': 2000000000000}},
            {'id': 'weekly', 'name': 'weekly', 'amount': {'usedFraction': 0.4}, 'window': {'durationMs': 10080*60*1000, 'resetsAt': 2000100000000}},
        ]}]}
        buckets = usage.parse_omp_usage(payload)
        result = usage.summarize('omp', buckets, 'test', 'fixture')
        self.assertEqual(result['five_hour_remaining_percent'], 75)
        self.assertEqual(result['weekly_remaining_percent'], 60)

    def test_omp_direct_wham_shape(self):
        payload = {'primary_window': {'used_percent': 10, 'limit_window_seconds': 18000, 'reset_at': 2000000000},
                   'secondary_window': {'used_percent': 20, 'limit_window_seconds': 604800, 'reset_at': 2000100000}}
        result = usage.summarize('omp', usage.parse_omp_usage(payload), 'test', 'fixture')
        self.assertEqual(result['five_hour_remaining_percent'], 90)
        self.assertEqual(result['weekly_remaining_percent'], 80)

    def test_process_classification(self):
        self.assertEqual(usage.classify_agent('/usr/bin/codex', ['codex']), 'codex')
        self.assertEqual(usage.classify_agent('/usr/local/bin/omp', ['omp']), 'omp')
        self.assertEqual(usage.classify_agent('/usr/bin/opencode2', ['opencode2']), 'opencode2')
        self.assertEqual(usage.classify_agent('/usr/bin/node', ['node', '/x/bin/codex']), 'codex')

    def test_missing_metrics_do_not_become_100_percent(self):
        result = usage.summarize('codex', [], 'test', 'fixture')
        self.assertEqual(result['state'], 'unknown')
        self.assertNotIn('five_hour_remaining_percent', result)


if __name__ == '__main__':
    unittest.main()
