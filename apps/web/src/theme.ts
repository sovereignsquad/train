import { createTheme } from "@mantine/core";

export const theme = createTheme({
  fontFamily: "var(--font-space-grotesk), sans-serif",
  fontFamilyMonospace: "var(--font-ibm-plex-mono), monospace",
  primaryColor: "green",
  defaultRadius: "md",
  autoContrast: true,
  headings: {
    fontFamily: "var(--font-space-grotesk), sans-serif",
  },
});
