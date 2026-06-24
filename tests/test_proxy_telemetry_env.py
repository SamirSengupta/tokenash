"""Tests for proxy telemetry environment variable handling."""

import asyncio
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tokenash.proxy.server import ProxyConfig, _proxy_config_from_env, create_app


class TestProxyTelemetrySDKEnv:
    """Test TOKENASH_SDK handling when the proxy builds telemetry beacons."""

    def test_proxy_telemetry_sdk_defaults_to_proxy(self, monkeypatch):
        """Telemetry beacon uses the default SDK label when env var is unset."""
        monkeypatch.delenv("TOKENASH_SDK", raising=False)

        with patch("tokenash.telemetry.beacon.TelemetryBeacon") as mock_beacon:
            create_app(
                ProxyConfig(
                    cache_enabled=False,
                    rate_limit_enabled=False,
                    cost_tracking_enabled=False,
                )
            )

        assert mock_beacon.call_args.kwargs["sdk"] == "proxy"

    def test_proxy_telemetry_sdk_uses_env_override(self, monkeypatch):
        """Telemetry beacon uses TOKENASH_SDK when it is non-empty."""
        monkeypatch.setenv("TOKENASH_SDK", "tokenash-app")

        with patch("tokenash.telemetry.beacon.TelemetryBeacon") as mock_beacon:
            create_app(
                ProxyConfig(
                    cache_enabled=False,
                    rate_limit_enabled=False,
                    cost_tracking_enabled=False,
                )
            )

        assert mock_beacon.call_args.kwargs["sdk"] == "tokenash-app"

    def test_proxy_telemetry_sdk_empty_env_falls_back_to_proxy(self, monkeypatch):
        """Telemetry beacon falls back to proxy when TOKENASH_SDK is blank."""
        monkeypatch.setenv("TOKENASH_SDK", "   ")

        with patch("tokenash.telemetry.beacon.TelemetryBeacon") as mock_beacon:
            create_app(
                ProxyConfig(
                    cache_enabled=False,
                    rate_limit_enabled=False,
                    cost_tracking_enabled=False,
                )
            )

        assert mock_beacon.call_args.kwargs["sdk"] == "proxy"


class TestProxyPeriodicTOINStatsEnv:
    """Test TOKENASH_PERIODIC_TOIN_STATS handling for long-lived proxy workers."""

    def test_periodic_toin_stats_enabled_by_default(self, monkeypatch):
        """Periodic TOIN stats logging remains enabled unless explicitly disabled."""
        monkeypatch.delenv("TOKENASH_PERIODIC_TOIN_STATS", raising=False)

        config = _proxy_config_from_env()

        assert config.periodic_toin_stats_enabled is True

    @pytest.mark.parametrize("value", ["0", "false", "off", "no"])
    def test_periodic_toin_stats_can_be_disabled_by_env(self, monkeypatch, value):
        """TOKENASH_PERIODIC_TOIN_STATS=0/false/off/no disables periodic logging."""
        monkeypatch.setenv("TOKENASH_PERIODIC_TOIN_STATS", value)

        config = _proxy_config_from_env()

        assert config.periodic_toin_stats_enabled is False

    def test_lifespan_skips_periodic_toin_stats_when_disabled(self, monkeypatch):
        """Disabling periodic TOIN stats avoids scheduling the stats loop."""
        monkeypatch.setenv("TOKENASH_SKIP_UPSTREAM_CHECK", "1")
        requested = False

        def fake_periodic_toin_stats():
            nonlocal requested
            requested = True

            async def noop():
                await asyncio.sleep(0)

            return noop()

        monkeypatch.setattr(
            "tokenash.proxy.server._log_toin_stats_periodically",
            fake_periodic_toin_stats,
        )

        app = create_app(
            ProxyConfig(
                optimize=False,
                cache_enabled=False,
                rate_limit_enabled=False,
                cost_tracking_enabled=False,
                periodic_toin_stats_enabled=False,
            )
        )

        with TestClient(app):
            pass

        assert requested is False

    def test_lifespan_schedules_periodic_toin_stats_when_enabled(self, monkeypatch):
        """Enabled periodic TOIN stats schedules the stats loop at startup."""
        monkeypatch.setenv("TOKENASH_SKIP_UPSTREAM_CHECK", "1")
        requested = False

        def fake_periodic_toin_stats():
            nonlocal requested
            requested = True

            async def noop():
                await asyncio.sleep(0)

            return noop()

        monkeypatch.setattr(
            "tokenash.proxy.server._log_toin_stats_periodically",
            fake_periodic_toin_stats,
        )

        app = create_app(
            ProxyConfig(
                optimize=False,
                cache_enabled=False,
                rate_limit_enabled=False,
                cost_tracking_enabled=False,
                periodic_toin_stats_enabled=True,
            )
        )

        with TestClient(app):
            pass

        assert requested is True
