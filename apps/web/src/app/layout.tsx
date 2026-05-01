import "@mantine/core/styles.css";
import "./globals.css";

import { ColorSchemeScript, MantineProvider, mantineHtmlProps } from "@mantine/core";
import type { Metadata } from "next";
import { IBM_Plex_Mono, Space_Grotesk } from "next/font/google";

import { theme } from "@/theme";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-ibm-plex-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "train operator",
  description: "Local operator dashboard for the train MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      {...mantineHtmlProps}
      className={`${spaceGrotesk.variable} ${ibmPlexMono.variable}`}
    >
      <head>
        <ColorSchemeScript defaultColorScheme="auto" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function () {
                const stored = window.localStorage.getItem("mantine-color-scheme-value") || "auto";
                const mode = stored === "auto"
                  ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "night" : "day")
                  : stored === "dark"
                    ? "night"
                    : "day";
                document.documentElement.dataset.theme = mode;
              })();
            `,
          }}
        />
      </head>
      <body>
        <MantineProvider theme={theme}>{children}</MantineProvider>
      </body>
    </html>
  );
}
