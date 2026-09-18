import random as rd
import time as tm
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import pyautogui as autogui


@dataclass
class ClickPreset:
    name: str
    x: int
    y: int


@dataclass
class AutomationConfig:
    browser: str
    search_text: str
    url: str
    repetitions: int
    wait_time: float
    default_click: Tuple[int, int]
    default_click_mode: str = "default"
    default_click_preset: str = ""
    click_presets: List[ClickPreset] = field(default_factory=list)
    custom_actions: str = ""


def _parse_click_coordinates(value: str) -> Tuple[int, int]:
    coords = [part.strip() for part in value.split(",")]
    if len(coords) != 2:
        raise ValueError(f"Coordenadas inválidas: {value}")
    return int(coords[0]), int(coords[1])


def _resolve_click_target(value: str, click_presets: Optional[Sequence[ClickPreset]] = None) -> Tuple[int, int]:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError("Coordenadas vazias.")

    lowered = normalized_value.lower()
    if lowered in {"off", "none", "desativado", "disabled"}:
        raise ValueError("Comando de clique desativado deve ser usado em 'default_click'.")

    if click_presets:
        matching_preset = next((preset for preset in click_presets if preset.name.lower() == lowered), None)
        if matching_preset is not None:
            return matching_preset.x, matching_preset.y

    if "," in normalized_value:
        return _parse_click_coordinates(normalized_value)

    raise ValueError(f"Coordenadas ou preset inválidos: {value}")


def build_action_plan(
    browser: str,
    search_text: str,
    wait_time: float,
    x: int,
    y: int,
    custom_actions: str,
    click_presets: Optional[Sequence[ClickPreset]] = None,
    default_click_mode: str = "default",
    default_click_preset: str = "",
) -> List[dict]:
    plan: List[dict] = []
    default_click = (int(x), int(y))
    resolved_default_click_mode = default_click_mode.lower() if default_click_mode else "default"

    if browser:
        plan.append({"type": "browser", "value": browser.lower()})

    if search_text.strip():
        plan.append({"type": "search", "value": search_text.strip()})

    if custom_actions:
        for line in custom_actions.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            command, _, value = line.partition(":")
            command = command.strip().lower()
            value = value.strip()

            if command in {"pesquisar", "search"}:
                plan.append({"type": "search", "value": value})
            elif command in {"url", "site", "open"}:
                plan.append({"type": "open_url", "value": value})
            elif command in {"esperar", "wait"}:
                plan.append({"type": "wait", "seconds": float(value)})
            elif command in {"clicar", "click", "clicks"}:
                entries = [entry.strip() for entry in value.split(";") if entry.strip()]
                if not entries:
                    raise ValueError(f"Nenhum clique informado: {value}")
                for entry in entries:
                    if click_presets and entry.lower() in {preset.name.lower() for preset in click_presets}:
                        matching_preset = next(preset for preset in click_presets if preset.name.lower() == entry.lower())
                        plan.append({"type": "click", "x": matching_preset.x, "y": matching_preset.y})
                    else:
                        x_value, y_value = _parse_click_coordinates(entry)
                        plan.append({"type": "click", "x": x_value, "y": y_value})
            elif command in {"preset", "ponto"}:
                preset_name = value
                matching_preset = None
                if click_presets:
                    matching_preset = next((preset for preset in click_presets if preset.name.lower() == preset_name.lower()), None)
                if matching_preset is None:
                    raise ValueError(f"Preset não encontrado: {preset_name}")
                plan.append({"type": "click", "x": matching_preset.x, "y": matching_preset.y})
            elif command in {"default_click", "click_padrao"}:
                lower_value = value.lower()
                if lower_value in {"off", "none", "desativado", "disabled"}:
                    resolved_default_click_mode = "off"
                elif click_presets:
                    matching_preset = next((preset for preset in click_presets if preset.name.lower() == lower_value), None)
                    if matching_preset is not None:
                        default_click = (matching_preset.x, matching_preset.y)
                        resolved_default_click_mode = "preset"
                    else:
                        default_click = _parse_click_coordinates(value)
                        resolved_default_click_mode = "coordinates"
                else:
                    default_click = _parse_click_coordinates(value)
                    resolved_default_click_mode = "coordinates"
            elif command in {"tecla", "key"}:
                plan.append({"type": "keypress", "value": value})
            elif command in {"hotkey", "shortcut"}:
                keys = [part.strip() for part in value.split(",") if part.strip()]
                plan.append({"type": "hotkey", "value": keys})
            elif command in {"enter", "enter_key"}:
                plan.append({"type": "keypress", "value": "enter"})

    if resolved_default_click_mode == "preset" and default_click_preset:
        matching_preset = next((preset for preset in (click_presets or []) if preset.name.lower() == default_click_preset.lower()), None)
        if matching_preset is not None:
            default_click = (matching_preset.x, matching_preset.y)

    if resolved_default_click_mode != "off":
        if resolved_default_click_mode == "preset" and default_click_preset:
            matching_preset = next((preset for preset in (click_presets or []) if preset.name.lower() == default_click_preset.lower()), None)
            if matching_preset is not None:
                default_click = (matching_preset.x, matching_preset.y)
        plan.append({"type": "click", "x": default_click[0], "y": default_click[1]})
    plan.append({"type": "wait", "seconds": float(wait_time)})
    return plan


class AutomationEngine:
    def __init__(self, status_callback=None):
        self.status_callback = status_callback

    def notify(self, message: str) -> None:
        if self.status_callback:
            self.status_callback(message)

    def run(self, config: AutomationConfig) -> None:
        self.notify("Iniciando automação universal...")
        autogui.PAUSE = 0.2

        if config.browser:
            self.open_browser(config.browser)

        for iteration in range(config.repetitions):
            self.notify(f"Iteração {iteration + 1} de {config.repetitions}")
            self.run_iteration(config)

        self.notify("Automação concluída.")

    def run_iteration(self, config: AutomationConfig) -> None:
        plan = build_action_plan(
            "",
            config.search_text,
            config.wait_time,
            config.default_click[0],
            config.default_click[1],
            config.custom_actions,
            config.click_presets,
            config.default_click_mode,
            config.default_click_preset,
        )

        for step in plan:
            step_type = step["type"]
            if step_type == "browser":
                self.open_browser(step["value"])
            elif step_type == "open_url":
                self.open_url(step["value"])
            elif step_type == "search":
                self.perform_search(step["value"])
            elif step_type == "wait":
                tm.sleep(step["seconds"])
            elif step_type == "click":
                autogui.click(step["x"], step["y"])
            elif step_type == "keypress":
                autogui.press(step["value"])
            elif step_type == "hotkey":
                autogui.hotkey(*step["value"])

        self.perform_loop_action(config.wait_time, config.default_click)

    def perform_loop_action(self, wait_time: float, default_click: Tuple[int, int]) -> None:
        tm.sleep(wait_time)
        numero_aleatorio = rd.randint(1, 500)
        autogui.write(str(numero_aleatorio + 1))
        tm.sleep(0.3)
        autogui.press("enter")
        autogui.click(default_click[0], default_click[1])

    def open_browser(self, browser_name: str) -> None:
        autogui.press("win")
        tm.sleep(0.4)
        autogui.write(browser_name)
        tm.sleep(0.4)
        autogui.press("enter")
        tm.sleep(2.0)

    def open_url(self, url: str) -> None:
        autogui.write(url)
        tm.sleep(0.3)
        autogui.press("enter")
        tm.sleep(1.5)

    def perform_search(self, text: str) -> None:
        autogui.write(text)
        tm.sleep(0.3)
        autogui.press("enter")
        tm.sleep(1.2)
