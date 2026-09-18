import unittest
from unittest.mock import patch

from app.automation_engine import AutomationConfig, AutomationEngine, ClickPreset, build_action_plan


class BuildActionPlanTests(unittest.TestCase):
    def test_default_click_can_be_disabled(self):
        plan = build_action_plan(
            browser="edge",
            search_text="python",
            wait_time=0.5,
            x=100,
            y=200,
            custom_actions="default_click: off",
            click_presets=[ClickPreset("canto", 50, 60)],
        )

        self.assertEqual(plan[-1], {"type": "wait", "seconds": 0.5})
        self.assertNotIn({"type": "click", "x": 100, "y": 200}, plan)

    def test_multiple_clicks_are_supported(self):
        plan = build_action_plan(
            browser="",
            search_text="",
            wait_time=0.2,
            x=999,
            y=888,
            custom_actions="clicks: 10,20; 30,40",
            click_presets=[],
        )

        self.assertIn({"type": "click", "x": 10, "y": 20}, plan)
        self.assertIn({"type": "click", "x": 30, "y": 40}, plan)
        self.assertIn({"type": "click", "x": 999, "y": 888}, plan)

    def test_preset_can_override_default_click(self):
        plan = build_action_plan(
            browser="",
            search_text="",
            wait_time=0.1,
            x=100,
            y=200,
            custom_actions="default_click: canto",
            click_presets=[ClickPreset("canto", 55, 66)],
        )

        self.assertIn({"type": "click", "x": 55, "y": 66}, plan)

    def test_browser_is_opened_only_once_per_run(self):
        engine = AutomationEngine()
        config = AutomationConfig(
            browser="edge",
            search_text="python",
            url="",
            repetitions=3,
            wait_time=0.1,
            default_click=(100, 200),
            click_presets=[],
            custom_actions="",
        )

        with patch.object(engine, "open_browser") as mock_open_browser, \
             patch.object(engine, "run_iteration") as mock_run_iteration:
            engine.run(config)

        self.assertEqual(mock_open_browser.call_count, 1)
        self.assertEqual(mock_run_iteration.call_count, 3)


if __name__ == "__main__":
    unittest.main()
