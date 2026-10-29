import pytest

from octop_gateway.channels.qq.channel import QQConfig


def test_social_trigger_switch_reads_nested_qq_group_policy() -> None:
    assert QQConfig.from_dict({}).social_trigger_enabled is True
    assert QQConfig.from_dict({"group_context": {"social_trigger_enabled": False}}).social_trigger_enabled is False
    assert QQConfig.from_dict({"group_context": {"social_trigger_enabled": True}}).social_trigger_enabled is True
    with pytest.raises(ValueError, match="social_trigger_enabled"):
        QQConfig.from_dict({"group_context": {"social_trigger_enabled": "false"}})
