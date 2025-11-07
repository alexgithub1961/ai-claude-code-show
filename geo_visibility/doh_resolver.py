"""
DNS-over-HTTPS Resolver
Bypasses UDP DNS blocking by using HTTPS (port 443) for DNS resolution
"""
import urllib.request
import json
import socket
from functools import lru_cache


class DoHResolver:
    """
    DNS-over-HTTPS resolver that works in restricted networks.

    Uses Cloudflare's DNS-over-HTTPS service to bypass UDP port 53 blocking.
    """

    def __init__(self, doh_server="https://cloudflare-dns.com/dns-query"):
        self.doh_server = doh_server
        self._original_getaddrinfo = None
        self._original_gethostbyname = None

    @lru_cache(maxsize=1000)
    def resolve(self, hostname):
        """
        Resolve hostname using DNS-over-HTTPS.

        Args:
            hostname: Domain name to resolve

        Returns:
            IP address string, or None if resolution fails
        """
        if not hostname:
            return None

        # Handle IP addresses (already resolved)
        try:
            socket.inet_aton(hostname)
            return hostname  # Already an IP
        except OSError:
            pass  # Not an IP, need to resolve

        # Query DNS-over-HTTPS
        url = f"{self.doh_server}?name={hostname}&type=A"

        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/dns-json')

            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

                if 'Answer' in data:
                    for answer in data['Answer']:
                        if answer.get('type') == 1:  # A record
                            return answer['data']

            return None
        except Exception as e:
            print(f"DoH resolution failed for {hostname}: {e}")
            return None

    def patch_socket(self):
        """
        Monkey-patch socket functions to use DNS-over-HTTPS.

        This makes ALL Python DNS resolution use DoH.
        Call this before using any network libraries.
        """
        self._original_getaddrinfo = socket.getaddrinfo
        self._original_gethostbyname = socket.gethostbyname

        def doh_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            """Patched getaddrinfo using DoH"""
            # Try DoH resolution
            ip = self.resolve(host)

            if ip:
                # Return fake getaddrinfo result
                return [
                    (socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))
                ]
            else:
                # Fall back to original (will likely fail, but worth trying)
                return self._original_getaddrinfo(host, port, family, type, proto, flags)

        def doh_gethostbyname(hostname):
            """Patched gethostbyname using DoH"""
            ip = self.resolve(hostname)
            if ip:
                return ip
            else:
                # Fall back to original
                return self._original_gethostbyname(hostname)

        # Apply patches
        socket.getaddrinfo = doh_getaddrinfo
        socket.gethostbyname = doh_gethostbyname

        print("✓ Socket patched to use DNS-over-HTTPS")
        print(f"  DoH Server: {self.doh_server}")

    def unpatch_socket(self):
        """Restore original socket functions"""
        if self._original_getaddrinfo:
            socket.getaddrinfo = self._original_getaddrinfo
        if self._original_gethostbyname:
            socket.gethostbyname = self._original_gethostbyname

        print("✓ Socket restored to original DNS")


# Global resolver instance
_resolver = DoHResolver()


def enable_doh():
    """
    Enable DNS-over-HTTPS for all Python network operations.

    Call this at the start of your program to bypass UDP DNS blocking.
    """
    _resolver.patch_socket()


def disable_doh():
    """Disable DNS-over-HTTPS and restore normal DNS"""
    _resolver.unpatch_socket()


def test_doh():
    """Test DNS-over-HTTPS functionality"""
    print("\n" + "="*70)
    print("Testing DNS-over-HTTPS Resolver")
    print("="*70 + "\n")

    resolver = DoHResolver()

    test_domains = [
        "google.com",
        "github.com",
        "openai.com",
    ]

    print("Testing direct DoH resolution:")
    for domain in test_domains:
        ip = resolver.resolve(domain)
        status = "✓" if ip else "✗"
        print(f"  {status} {domain:20} → {ip or 'FAILED'}")

    print("\nTesting patched socket module:")
    resolver.patch_socket()

    import socket as sock
    for domain in test_domains:
        try:
            ip = sock.gethostbyname(domain)
            print(f"  ✓ {domain:20} → {ip}")
        except Exception as e:
            print(f"  ✗ {domain:20} → FAILED: {e}")

    resolver.unpatch_socket()

    print("\n" + "="*70)
    print("DoH Test Complete")
    print("="*70)


if __name__ == "__main__":
    test_doh()
