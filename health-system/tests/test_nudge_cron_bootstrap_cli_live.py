from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import patch

from runtime import nudge_cron_bootstrap


class NudgeCronBootstrapCliLiveTests(unittest.TestCase):
    def test_main_wires_sessions_send_tool_in_live_session_mode(self):
        captured = {}

        def fake_execute(slot, channel, recipient, **kwargs):
            captured['slot'] = slot
            captured['channel'] = channel
            captured['recipient'] = recipient
            captured['sessions_send_tool'] = kwargs.get('sessions_send_tool')
            return {
                'selection': {'send': True, 'skip_reason': None},
                'log': {
                    'runtime_mode': 'orchestrated',
                    'state_source': 'persisted',
                    'activity_source': 'persisted',
                    'recent_user_activity_count': 0,
                    'transport': 'openclaw_session',
                    'launcher_mode': 'live_session',
                }
            }

        fake_functions = types.ModuleType('functions')
        fake_functions.sessions_send = lambda **kwargs: {'ok': True}
        with patch.dict(sys.modules, {'functions': fake_functions}):
            with patch('runtime.nudge_cron_bootstrap.execute_slot', side_effect=fake_execute):
                rc = nudge_cron_bootstrap.main([
                    '--slot', 'morning_plan_check',
                    '--exec-mode', 'live_session',
                    '--channel', 'openclaw_session',
                    '--recipient', 'scheduled-health-session',
                ])
        self.assertEqual(rc, 0)
        self.assertEqual(captured['slot'], 'morning_plan_check')
        self.assertEqual(captured['channel'], 'openclaw_session')
        self.assertIsNotNone(captured['sessions_send_tool'])


if __name__ == '__main__':
    unittest.main()
