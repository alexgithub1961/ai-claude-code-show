# Docker DNS Resolution Fix
## Solving "ERR_NAME_NOT_RESOLVED" for Browser Searches

**Problem**: Playwright browser in Docker container cannot resolve google.com
```
ERR_NAME_NOT_RESOLVED at https://www.google.com/
```

---

## Quick Fixes

### Method 1: Use Host's DNS (Recommended)

```bash
# When running Docker container, add DNS servers:
docker run --dns 8.8.8.8 --dns 8.8.4.4 <your-image>

# Or use host's network:
docker run --network=host <your-image>
```

### Method 2: Configure Docker Daemon

Edit `/etc/docker/daemon.json`:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
```

Then restart Docker:
```bash
sudo systemctl restart docker
```

### Method 3: Fix Inside Container

```bash
# Inside running container:
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf
```

---

## Detailed Solutions

### Solution 1: Docker Run with DNS

**For interactive sessions**:
```bash
docker run -it --rm \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -v $(pwd):/workspace \
  <your-image> \
  bash

# Then inside container:
cd /workspace/geo_visibility
./quick_start.sh
```

**For docker-compose**:
```yaml
version: '3.8'
services:
  geo-assessment:
    image: your-image
    dns:
      - 8.8.8.8
      - 8.8.4.4
      - 1.1.1.1
    volumes:
      - ./geo_visibility:/workspace
```

### Solution 2: Use Host Network Mode

**Advantages**: Uses host's networking stack directly
**Disadvantages**: Less isolation, may conflict with host ports

```bash
docker run -it --rm \
  --network=host \
  -v $(pwd):/workspace \
  <your-image> \
  bash
```

### Solution 3: Fix /etc/resolv.conf

**In Dockerfile**:
```dockerfile
FROM python:3.11

# Fix DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf && \
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Install dependencies
RUN pip install playwright httpx
RUN playwright install chromium

WORKDIR /workspace
```

**At runtime** (temporary):
```bash
# Inside container:
cat > /etc/resolv.conf << EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
EOF
```

### Solution 4: Check Docker Bridge Network

```bash
# Check Docker network settings
docker network inspect bridge

# Look for DNS settings in output
# If empty, configure Docker daemon

# Test DNS resolution inside container
docker run --rm alpine nslookup google.com

# If that works, issue is with Playwright, not Docker
```

---

## Testing DNS Resolution

### Test 1: Basic Ping
```bash
# Inside container:
ping -c 3 google.com
ping -c 3 8.8.8.8

# If google.com fails but 8.8.8.8 works = DNS issue
# If both fail = network issue
# If both work = Playwright issue
```

### Test 2: DNS Lookup
```bash
# Inside container:
nslookup google.com
dig google.com

# Should return IP addresses
```

### Test 3: Python HTTP Request
```python
# Inside container:
python3 -c "
import httpx
response = httpx.get('https://www.google.com')
print(f'Status: {response.status_code}')
print('Success!' if response.status_code == 200 else 'Failed!')
"
```

### Test 4: Playwright with DNS Test
```python
# test_dns_playwright.py
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto("https://www.google.com", timeout=10000)
            print("✓ Successfully reached google.com")
            title = await page.title()
            print(f"✓ Page title: {title}")
        except Exception as e:
            print(f"✗ Failed: {e}")
        finally:
            await browser.close()

asyncio.run(test())
```

---

## Common DNS Servers

**Google DNS** (Most common):
- Primary: 8.8.8.8
- Secondary: 8.8.4.4

**Cloudflare DNS** (Privacy-focused):
- Primary: 1.1.1.1
- Secondary: 1.0.0.1

**Quad9** (Security-focused):
- Primary: 9.9.9.9
- Secondary: 149.112.112.112

**OpenDNS**:
- Primary: 208.67.222.222
- Secondary: 208.67.220.220

---

## Docker Compose Full Example

```yaml
version: '3.8'

services:
  geo-assessment:
    image: python:3.11

    # DNS configuration
    dns:
      - 8.8.8.8
      - 8.8.4.4
      - 1.1.1.1

    # Alternative: use host network
    # network_mode: "host"

    volumes:
      - ./geo_visibility:/workspace

    working_dir: /workspace

    environment:
      - SEARCHAPI_API_KEY=${SEARCHAPI_API_KEY}

    command: |
      bash -c "
        pip install playwright httpx &&
        playwright install chromium &&
        python browser_search_engine.py
      "
```

Run with:
```bash
export SEARCHAPI_API_KEY=dUngVqvqnKPAr1p1BKqKENJW
docker-compose up
```

---

## Troubleshooting

### Issue: "ERR_NAME_NOT_RESOLVED"

**Diagnosis**:
```bash
# 1. Check if DNS is configured
cat /etc/resolv.conf

# 2. Test DNS resolution
nslookup google.com

# 3. Test with different DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
nslookup google.com
```

**Solutions**:
1. Add `--dns 8.8.8.8` to docker run
2. Use `--network=host`
3. Configure Docker daemon DNS
4. Fix /etc/resolv.conf in container

### Issue: "Connection timeout"

**Diagnosis**:
```bash
# Test if Google is reachable
curl -v https://www.google.com

# Check if firewall blocking
iptables -L
```

**Solutions**:
1. Check firewall rules
2. Check proxy settings
3. Try different network mode
4. Check if running in restricted environment

### Issue: "Cannot install Chromium"

**Diagnosis**:
```bash
# Check available disk space
df -h

# Check if running as root
whoami

# Try manual install
python3 -m playwright install chromium --verbose
```

**Solutions**:
1. Ensure sufficient disk space (1GB+)
2. Run as root or with proper permissions
3. Check internet connectivity during install

---

## For Sandboxed/Restricted Environments

If you're in a highly restricted environment (like certain CI/CD or sandboxed containers):

### Option 1: Use a Proxy
```bash
docker run --rm \
  -e HTTP_PROXY=http://proxy:port \
  -e HTTPS_PROXY=http://proxy:port \
  --dns 8.8.8.8 \
  <your-image>
```

### Option 2: Run on Host
```bash
# Instead of Docker, run directly on host
cd geo_visibility
pip install playwright httpx
playwright install chromium
python browser_search_engine.py
```

### Option 3: Use Local DNS Cache
```bash
# Start local DNS cache
docker run -d --name dns-cache \
  -p 53:53/udp \
  andyshinn/dnsmasq:2.78

# Use it in your container
docker run --rm \
  --dns $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dns-cache) \
  <your-image>
```

---

## Current Claude Code Environment

**Status**: Running in sandboxed Docker environment

**Issue**: Cannot resolve DNS (ERR_NAME_NOT_RESOLVED)

**Why**: Container likely doesn't have DNS configured or network access is restricted

**Solutions to try**:
1. Ask Claude Code to restart with DNS flags
2. Run assessment outside Claude Code environment
3. Use host machine directly
4. Request network access configuration

**Workaround**:
Export the code and run on local machine or cloud VM:
```bash
# On your local machine:
git clone <repo>
cd geo_visibility
pip install playwright httpx
playwright install chromium
./quick_start.sh
```

---

## Verifying the Fix

After applying a fix, verify with this test script:

```bash
# test_network.sh
#!/bin/bash

echo "Testing network connectivity..."

echo -n "1. Ping Google DNS (8.8.8.8): "
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "✓ OK"
else
    echo "✗ FAIL"
fi

echo -n "2. Ping google.com: "
if ping -c 1 google.com &> /dev/null; then
    echo "✓ OK"
else
    echo "✗ FAIL (DNS issue)"
fi

echo -n "3. HTTP to google.com: "
if curl -s -o /dev/null -w "%{http_code}" https://www.google.com | grep -q "200"; then
    echo "✓ OK"
else
    echo "✗ FAIL"
fi

echo -n "4. Playwright test: "
python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto('https://www.google.com', timeout=5000)
            await browser.close()
            return True
    except:
        return False

result = asyncio.run(test())
print('✓ OK' if result else '✗ FAIL')
" 2>/dev/null || echo "✗ FAIL"

echo ""
echo "If all tests pass, browser search should work!"
```

---

## Quick Reference

| Method | Command | Pros | Cons |
|--------|---------|------|------|
| **--dns flag** | `docker run --dns 8.8.8.8` | Simple, no daemon change | Per-run only |
| **--network=host** | `docker run --network=host` | Uses host network | Less isolation |
| **/etc/resolv.conf** | `echo "nameserver 8.8.8.8" > /etc/resolv.conf` | Quick fix | Temporary |
| **daemon.json** | Edit `/etc/docker/daemon.json` | Permanent, all containers | Requires restart |
| **docker-compose** | `dns: [8.8.8.8]` in yaml | Reproducible | Needs compose file |

**Recommended for one-off tests**: `docker run --dns 8.8.8.8 --dns 8.8.4.4`

**Recommended for persistent setup**: Edit `/etc/docker/daemon.json`

---

## Summary

1. **Quick fix**: `docker run --dns 8.8.8.8 --dns 8.8.4.4 ...`
2. **Test**: `ping google.com` inside container
3. **Verify**: Run `python browser_search_engine.py`
4. **If still fails**: Try `--network=host` mode

**For Claude Code environment**: May need to run assessment outside container on host machine or cloud VM.
