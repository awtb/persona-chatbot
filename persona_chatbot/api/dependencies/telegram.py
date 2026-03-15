from collections.abc import Callable
from ipaddress import AddressValueError
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network

from aiogram import Bot
from aiogram import Dispatcher
from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from fastapi import Request
from fastapi import status

from persona_chatbot.api.dependencies.common import get_settings
from persona_chatbot.settings import Settings

TELEGRAM_TRUSTED_NETWORKS = [
    "149.154.160.0/20",
    "91.108.4.0/22",
]


def get_dispatcher(
    request: Request,
) -> Dispatcher:
    """
    Returns initialized `Dispatcher` object
    :return:
    """
    return request.app.state.dispatcher


def get_bot(request: Request) -> Bot:
    """
    Returns initialized `Bot` object
    :return:
    """
    return request.app.state.bot


def cidr(src: str) -> Callable[[str], bool]:
    network: IPv4Network | IPv6Network
    try:
        network = IPv4Network(src)
    except AddressValueError:
        network = IPv6Network(src)

    def predicate(ip: str) -> bool:
        addr: IPv4Address | IPv6Address
        try:
            addr = IPv4Address(ip)
        except AddressValueError:
            addr = IPv6Address(ip)

        return addr in network

    return predicate


TELEGRAM_PREDICATES = tuple(map(cidr, TELEGRAM_TRUSTED_NETWORKS))


def is_telegram_subnet(ip: str) -> bool:
    """
    Is request incomes from Telegram?
    :param ip: IP Address
    """
    return any(pred(ip) for pred in TELEGRAM_PREDICATES)


def validate_tg_request(request: Request) -> None:
    """
    Dependency, inject it for validating Telegram's subnets
    :param request: A request
    :raises HTTPException: If request was not created for Telegram's subnets
    """
    if not is_telegram_subnet(request.client.host):
        raise HTTPException(
            detail="Only `Telegram` can make requests.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


def validate_tg_webhook_token(
    secret_token: str = Header(
        validation_alias="X-Telegram-Bot-Api-Secret-Token",
    ),
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.tg_bot_webhook_token != secret_token:
        raise HTTPException(
            detail="Seriously?",
            status_code=status.HTTP_403_FORBIDDEN,
        )


def get_telegram_bot(request: Request) -> Bot:
    return request.app.state.tg_bot


def get_telegram_dispatcher(request: Request) -> Dispatcher:
    return request.app.state.tg_dispatcher
