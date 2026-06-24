import { afterEach, describe, expect, it, vi } from "vitest";

import { TokenashPlugin } from "./plugin.js";

function pluginInput() {
  return {
    client: {},
    project: { id: "project-1" },
    directory: "/repo",
    worktree: "/repo",
    experimental_workspace: {
      register: vi.fn(),
    },
    $: {},
  } as never;
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("TokenashPlugin", () => {
  it("adds only Tokenash metadata to shell env", async () => {
    const plugin = await TokenashPlugin(pluginInput(), {
      proxyUrl: "http://127.0.0.1:8787/",
      backend: "litellm",
    });
    const output = {
      env: {
        OPENAI_BASE_URL: "https://deepseek.example/v1",
        ANTHROPIC_BASE_URL: "https://anthropic.example",
      },
    };

    await plugin["shell.env"]?.({ cwd: "/repo" }, output);

    expect(output.env).toMatchObject({
      TOKENASH_ACTIVE: "1",
      TOKENASH_PROXY_URL: "http://127.0.0.1:8787",
      TOKENASH_PROJECT: "project-1",
      TOKENASH_BACKEND: "litellm",
      OPENAI_BASE_URL: "https://deepseek.example/v1",
      ANTHROPIC_BASE_URL: "https://anthropic.example",
    });
  });

  it("exposes a tokenash_retrieve tool backed by the proxy", async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => "original content",
    }));
    vi.stubGlobal("fetch", fetchMock);

    const plugin = await TokenashPlugin(pluginInput(), {
      proxyUrl: "http://127.0.0.1:8787",
    });
    const result = await plugin.tool?.tokenash_retrieve.execute(
      { hash: "0123456789abcdef01234567", query: "needle" },
      {} as never,
    );

    expect(result).toBe("original content");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8787/v1/retrieve/0123456789abcdef01234567?query=needle",
      expect.any(Object),
    );
  });
});
