"use client";

import { ActionIcon, Tooltip, useMantineColorScheme } from "@mantine/core";
import { useEffect } from "react";

type ThemeMode = "auto" | "light" | "dark";

function nextTheme(mode: ThemeMode): ThemeMode {
  switch (mode) {
    case "auto":
      return "light";
    case "light":
      return "dark";
    case "dark":
      return "auto";
  }
}

function labelFor(mode: ThemeMode): string {
  switch (mode) {
    case "auto":
      return "Theme: Auto";
    case "light":
      return "Theme: Light";
    case "dark":
      return "Theme: Dark";
  }
}

function iconFor(mode: ThemeMode): string {
  switch (mode) {
    case "auto":
      return "◐";
    case "light":
      return "☼";
    case "dark":
      return "☾";
  }
}

export function ThemeToggle() {
  const { colorScheme, setColorScheme } = useMantineColorScheme();
  const mode = colorScheme as ThemeMode;

  useEffect(() => {
    const effective =
      mode === "auto"
        ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "night" : "day")
        : mode === "dark"
          ? "night"
          : "day";
    document.documentElement.dataset.theme = effective;
  }, [mode]);

  return (
    <Tooltip label={labelFor(mode)}>
      <ActionIcon
        aria-label={labelFor(mode)}
        className="theme-toggle"
        onClick={() => setColorScheme(nextTheme(mode))}
        radius="xl"
        size="lg"
        variant="subtle"
      >
        {iconFor(mode)}
      </ActionIcon>
    </Tooltip>
  );
}
