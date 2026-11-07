"""Forwards requests, websockets included, to the dashboard."""

import asyncio
from typing import Awaitable, Callable, Mapping

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType, web
from yarl import URL

# Host is kept, so the dashboard builds its URLs, like a login's `next`, with
# the public address rather than its own.
HOP_HEADERS = {
    "connection",
    "upgrade",
    "keep-alive",
    "transfer-encoding",
    "content-length",
    "content-encoding",
    "sec-websocket-key",
    "sec-websocket-version",
    "sec-websocket-extensions",
    "sec-websocket-accept",
}

CLIENT_SESSION = web.AppKey("proxy_client_session", ClientSession)

Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def _headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in HOP_HEADERS}


async def client_session(app: web.Application):
    """Open the session the proxy forwards with, for the app's lifetime."""
    app[CLIENT_SESSION] = ClientSession()
    yield
    await app[CLIENT_SESSION].close()


def proxy_to(upstream: URL) -> Handler:
    """A handler forwarding each request to the same path on `upstream`."""

    async def handler(request: web.Request) -> web.StreamResponse:
        session = request.app[CLIENT_SESSION]
        target = upstream.join(request.rel_url)

        if request.headers.get("Upgrade", "").lower() == "websocket":
            return await _websocket(request, session, target.with_scheme("ws"))

        async with session.request(
            request.method,
            target,
            headers=_headers(request.headers),
            data=await request.read(),
            allow_redirects=False,
        ) as response:
            return web.Response(
                status=response.status,
                body=await response.read(),
                headers=_headers(response.headers),
            )

    return handler


async def _websocket(
    request: web.Request, session: ClientSession, target: URL
) -> web.WebSocketResponse:
    client = web.WebSocketResponse()
    await client.prepare(request)

    async with session.ws_connect(target, headers=_headers(request.headers)) as server:
        pumps = [
            asyncio.create_task(_pump(client, server)),
            asyncio.create_task(_pump(server, client)),
        ]
        # One side closing closes the other.
        await asyncio.wait(pumps, return_when=asyncio.FIRST_COMPLETED)

        for pump in pumps:
            pump.cancel()

    await client.close()

    return client


async def _pump(
    source: web.WebSocketResponse | ClientWebSocketResponse,
    sink: web.WebSocketResponse | ClientWebSocketResponse,
) -> None:
    async for message in source:
        if message.type == WSMsgType.TEXT:
            await sink.send_str(message.data)
        elif message.type == WSMsgType.BINARY:
            await sink.send_bytes(message.data)
