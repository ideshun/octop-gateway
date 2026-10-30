# Pre-agent admission

Pass an `AdmissionHandler` as `ChannelManager(inbound_handler=...)`, or use
`manager.set_inbound_handler(handler)` to replace/clear it. Each accepted input
passes through the hook before session batching and model processing.

```python
async def admission(channel, message, dispatch):
    # Return True to claim input, False to retain native routing.
    return False

manager.set_inbound_handler(admission)
```

The hook may retain `dispatch` for a bounded delayed task. Dispatch holds the
channel/session lock and refuses removed or replaced channels and stopped
managers. `activate=True` only activates groups with group policy enabled and
visibility `all`; native sender checks and tool ceilings still apply. The host
must cancel its plugin tasks before stopping the manager or unloading plugins.

`InboundReceipt` records `attempted` and `delivered` separately. A send failure
after an attempt is not proof of non-delivery; callers must not blindly resend.
Cancellation propagates. Ordinary group input fails closed on hook errors;
native commands, direct messages and mentions retain normal routing. The default
without a hook preserves existing batching and routing behavior.

After a handler claims input, the manager calls the adapter's synchronous
`on_inbound_claimed(message)` hook. Durable adapters can release their intake
slot here; they must preserve an already started or completed message if the
handler dispatched synchronously. A later dispatch still follows the normal
preparation, processing and completion lifecycle.

Group participation policies use the same hook across channel types. Adapters
must provide stable subject and sender IDs plus explicit boolean
`bot_mentioned` and `sender_is_bot` metadata. An adapter may instead expose
`async resolve_sender_is_bot(message) -> bool | None`; unknown identities are
not evidence of a human sender. Ordinary messages must reach the hook before
the native activation check without bypassing sender or command permissions.
`BaseChannel.plugin_group_settings` exposes persisted boolean switches under
`group_context`, including switches contributed by policy plugins; it does not
change the platform's message access permissions.

## QQ group metadata

`await qq_channel.get_group_info(group_openid)` returns the official QQ response,
including `group_name`, but not the numeric QQ group number. Only platform-
allowlisted bots may call this API; QQ code `11253` means permission is missing.
The channel enforces a separate 30-request/minute sliding window including
token retries. A caller sharing one bot across several channel instances must
coordinate that bot's combined quota. Waiting for a quota slot is cancellable;
UI callers should apply a timeout and cache metadata rather than query on every
message. The lookup does not change message receiving or sending behavior.

Official reference: https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_info.get.html
