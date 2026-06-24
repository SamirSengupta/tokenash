import { installTokenashTransport } from "../dist/index.js";

const proxyUrl = process.env.TOKENASH_OPENCODE_TRANSPORT_PROXY_URL;
if (!proxyUrl) {
  throw new Error("Tokenash OpenCode transport shim loaded without TOKENASH_OPENCODE_TRANSPORT_PROXY_URL");
}

installTokenashTransport({ proxyUrl });
