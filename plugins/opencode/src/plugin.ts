import type { Plugin } from "@opencode-ai/plugin";
import { tool } from "@opencode-ai/plugin";
import { z } from "zod";

import { createTokenashRetrieveTool, getDefaultProxyUrl } from "./retrieve.js";
import { installTokenashTransport } from "./transport.js";

export interface TokenashOpenCodePluginOptions {
  proxyUrl?: string;
  project?: string;
  backend?: string;
  debug?: boolean;
}

function normalizeProxyUrl(url: string): string {
  return url.replace(/\/+$/, "");
}

function resolveProxyUrl(options?: TokenashOpenCodePluginOptions): string {
  return normalizeProxyUrl(
    options?.proxyUrl ??
      process.env.TOKENASH_PROXY_URL ??
      process.env.TOKENASH_BASE_URL ??
      getDefaultProxyUrl(),
  );
}

export const TokenashPlugin: Plugin = async (input, options = {}) => {
  const pluginOptions = options as TokenashOpenCodePluginOptions;
  const proxyUrl = resolveProxyUrl(pluginOptions);
  const retrieveTool = createTokenashRetrieveTool({ proxyBaseUrl: proxyUrl });
  const uninstallTransport = installTokenashTransport({
    proxyUrl,
    debug: pluginOptions.debug,
  });

  return {
    dispose: async () => {
      uninstallTransport();
    },
    tool: {
      tokenash_retrieve: tool({
        description: retrieveTool.description,
        args: {
          hash: z
            .string()
            .regex(/^[a-f0-9]{24}$/i, "Expected 24-character hex hash"),
          query: z.string().optional(),
        },
        async execute(args) {
          return retrieveTool.execute(args);
        },
      }),
    },
    "shell.env": async (_input, output) => {
      output.env.TOKENASH_ACTIVE = "1";
      output.env.TOKENASH_PROXY_URL = proxyUrl;
      output.env.TOKENASH_PROJECT =
        pluginOptions.project ??
        (input.project as { id?: string }).id ??
        input.directory;
      if (pluginOptions.backend) {
        output.env.TOKENASH_BACKEND = pluginOptions.backend;
      }
    },
  };
};

export default TokenashPlugin;
