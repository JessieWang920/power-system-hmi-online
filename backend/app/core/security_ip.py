# backend/app/core/security.py
import ipaddress
from fastapi import Request, HTTPException, status
from .config import settings

_whitelist = [
    ipaddress.ip_network(net.strip())
    for net in settings().allowed_ips.split(",")
]

def ip_whitelist(request: Request):
    ip = ipaddress.ip_address(request.client.host)
    if not any(ip in net for net in _whitelist):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"IP {ip} 不在白名單"
        )
