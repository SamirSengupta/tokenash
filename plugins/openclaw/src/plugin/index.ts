/**
 * Tokenash OpenClaw Plugin — register ContextEngine + CCR retrieval tool.
 *
 * Usage:
 *   openclaw plugins install tokenash/openclaw
 *
 * Configuration (in ~/.openclaw/config.json or ~/.clawdbot/clawdbot.json):
 *   {
 *     "plugins": {
 *       "slots": { "contextEngine": "tokenash" },
 *       "entries": { "tokenash": { "enabled": true } }
 *     }
 *   }
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { TokenashContextEngine } from "../engine.js";
import {
  applyGatewayProviderBaseUrlsInPlace,
  resolveGatewayProviderIds,
} from "../gateway-config.js";
import { normalizeAndValidateProxyUrl, probeTokenashProxy } from "../proxy-manager.js";
import { createTokenashRetrieveTool } from "../tools/tokenash-retrieve.js";

/**
 * OpenClaw 2026.x plugin API requires a `{ register(api) }` object export.
 * The previous bare-function default export was silently skipped by the loader.
 * See: https://github.com/SamirSengupta/tokenash/issues/XXX
 */
export default {
  register: tokenashPlugin,
};

function tokenashPlugin(api: any) {
  const config = api.config?.plugins?.entries?.tokenash?.config ?? {};
  const logger = api.logger ?? console;
  const rawProxyUrl = config.proxyUrl;
  const proxyUrl =
    typeof rawProxyUrl === "string" && rawProxyUrl.trim().length > 0
      ? normalizeAndValidateProxyUrl(rawProxyUrl)
      : undefined;

  const engine = new TokenashContextEngine({ ...config, proxyUrl }, {
    info: (m: string) => logger.info(m),
    warn: (m: string) => logger.warn(m),
    error: (m: string) => logger.error(m),
    debug: (m: string) => logger.debug?.(m),
  });
  const gatewayProviderIds = resolveGatewayProviderIds(config);
  let validatedConfiguredProxyUrl: string | null = null;
  let configuredProxyProbePromise: Promise<string | null> | null = null;

  const applyGatewayRouting = async (activeProxyUrl: string) => {
    if (gatewayProviderIds.length === 0) {
      return;
    }

    try {
      const changed = applyGatewayProviderBaseUrlsInPlace(api.config, activeProxyUrl, gatewayProviderIds);

      if (changed) {
        logger.info(
          `[tokenash] Routed ${gatewayProviderIds.join(", ")} through Tokenash proxy in memory at ${activeProxyUrl}`,
        );
      } else {
        logger.info(
          `[tokenash] Upstream gateway already routed in memory for ${gatewayProviderIds.join(", ")} at ${activeProxyUrl}`,
        );
      }
    } catch (error) {
      logger.warn(`[tokenash] Failed to configure upstream gateway routing: ${error}`);
    }
  };

  const getConfiguredRoutingProxyUrl = async (): Promise<string | null> => {
    if (!proxyUrl) {
      return null;
    }
    if (validatedConfiguredProxyUrl === proxyUrl) {
      return validatedConfiguredProxyUrl;
    }
    if (!configuredProxyProbePromise) {
      configuredProxyProbePromise = probeTokenashProxy(proxyUrl)
        .then((probe) => {
          if (probe.reachable && probe.isTokenash) {
            validatedConfiguredProxyUrl = proxyUrl;
            return proxyUrl;
          }
          logger.warn(
            `[tokenash] Skipping upstream gateway routing: configured proxyUrl is not a ready Tokenash proxy at ${proxyUrl}` +
              (probe.reason ? ` (${probe.reason})` : ""),
          );
          return null;
        })
        .catch((error) => {
          logger.warn(
            `[tokenash] Skipping upstream gateway routing: failed to probe configured proxyUrl ${proxyUrl}: ${error}`,
          );
          return null;
        })
        .finally(() => {
          configuredProxyProbePromise = null;
        });
    }
    return configuredProxyProbePromise;
  };

  const ensureGatewayRouting = async () => {
    if (gatewayProviderIds.length === 0) {
      return;
    }
    const activeProxyUrl = engine.getProxyUrl() ?? (await getConfiguredRoutingProxyUrl());
    if (!activeProxyUrl) {
      logger.debug?.("[tokenash] Deferring upstream gateway routing until proxy is available");
      return;
    }
    await applyGatewayRouting(activeProxyUrl);
  };

  engine.onProxyReady(async (activeProxyUrl) => {
    await applyGatewayRouting(activeProxyUrl);
  });

  // Register as context engine
  api.registerContextEngine("tokenash", () => engine);

  // Register CCR retrieval tool (active once proxy is running)
  api.registerTool((ctx: any) => {
    const activeProxyUrl = engine.getProxyUrl() ?? proxyUrl;
    if (!activeProxyUrl) return null;
    return createTokenashRetrieveTool({ proxyUrl: activeProxyUrl });
  }, { names: ["tokenash_retrieve"] });

  api.on("gateway_start", async () => {
    await ensureGatewayRouting();
  });

  void ensureGatewayRouting();

  logger.info("[tokenash] Plugin registered");
}
