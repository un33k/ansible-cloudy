# UFW Rework Plan

## Overview
This document outlines the rework of UFW (Uncomplicated Firewall) management in ansible-cloudy to handle complex scenarios including Docker integration, dynamic ports, and safe re-runs.

## Current Issues
1. Security playbook enables UFW with default deny, potentially breaking existing services
2. No consideration for Docker's UFW chain modifications  
3. No handling of dynamic ports (VPN, containers)
4. Each service manages its own UFW rules independently
5. Re-running security playbook could reset configurations

## Proposed Architecture

### 1. UFW State Management
Create a UFW state detection and preservation system:
- Check if UFW is installed AND enabled
- Capture existing rules before any modifications
- Provide options: preserve, merge, or reset

### 2. Layered UFW Configuration

#### Base Layer (security.yml):
- Install UFW (if not present)
- Configure logging
- Set defaults (if not already set)
- Ensure SSH port is allowed
- DO NOT enable if already enabled with rules

#### Service Layer (per service):
- Add service-specific rules
- Never reset or disable UFW
- Tag rules with service name for tracking

#### Application Layer:
- Dynamic port management
- Docker integration aware

### 3. Docker Integration
Docker creates its own iptables chains (DOCKER, DOCKER-USER) that must be preserved:

```yaml
# New task: tasks/sys/firewall/docker-aware-config.yml
- Check for Docker iptables chains
- Preserve DOCKER-USER rules
- Configure UFW to work with Docker networking
```

**Docker UFW Flow:**
```
[Client] -> Internet -> [Host UFW] -> [Docker iptables] -> [Container]
                           |                    |
                     (Port 443 open)     (NAT to container:443)
```

### 4. Dynamic Port Handling
For services like VPN with dynamic ports:

```yaml
# tasks/sys/firewall/allow-dynamic-range.yml
- name: Allow dynamic port range
  ufw:
    rule: allow
    port: "{{ start_port }}:{{ end_port }}"
    proto: "{{ proto }}"
    comment: "{{ service_name }} dynamic ports"
```

### 5. UFW Rule Tagging
Implement rule comments for tracking which service added which rule:

```yaml
ufw:
  rule: allow
  port: 443
  comment: "nginx-https"  # Service identifier
```

### 6. Safe Re-run Strategy

```yaml
# In security.yml
- name: Check UFW current state
  command: ufw status numbered
  register: ufw_current_state
  
- name: Determine UFW strategy
  set_fact:
    ufw_strategy: >-
      {%- if 'inactive' in ufw_current_state.stdout -%}
        fresh_install
      {%- elif ufw_rule_count | int > 5 -%}
        preserve_existing
      {%- else -%}
        merge_rules
      {%- endif -%}
```

## Implementation Plan

### Phase 1: State Detection
1. Create `cloudy/tasks/sys/firewall/check-state.yml`
   - Detect UFW installation status
   - Check if UFW is enabled
   - Count existing rules
   - Detect Docker iptables chains

### Phase 2: Rule Preservation
2. Create `cloudy/tasks/sys/firewall/preserve-rules.yml`
   - Backup existing UFW rules
   - Parse rules for service tags
   - Create restoration capability

### Phase 3: Docker Integration
3. Create `cloudy/tasks/sys/firewall/docker-aware-config.yml`
   - Detect Docker installation
   - Check Docker iptables chains
   - Configure UFW to coexist with Docker
   - Handle Docker published ports

### Phase 4: Dynamic Ports
4. Create `cloudy/tasks/sys/firewall/allow-dynamic-range.yml`
   - Support port ranges
   - Tag with service names
   - Handle TCP/UDP protocols

### Phase 5: Update Security Playbook
5. Modify `cloudy/playbooks/recipes/core/security.yml`
   - Implement state detection
   - Add preservation logic
   - Make UFW enabling conditional

### Phase 6: Centralize Defaults
6. Create `cloudy/defaults/firewall.yml`
   - UFW default policies
   - Standard port definitions
   - Docker integration flags

## Key Principles

1. **Idempotent**: Running multiple times produces same result
2. **Non-destructive**: Never break existing working configurations  
3. **Service-aware**: Each service manages its own rules
4. **Docker-friendly**: Respect Docker's iptables modifications
5. **Auditable**: Track which service added which rules

## Complex Scenarios

### Scenario 1: Docker with Dynamic VPN
```
[Client] -> [UFW:1194] -> [Host] -> [Docker NAT] -> [OpenVPN Container]
                             |
                    [UFW:32768-60999] -> [Dynamic client ports]
```

### Scenario 2: Multiple Docker Services
```
[Internet] -> [UFW:80,443] -> [Host] -> [Docker] -> [nginx:80,443]
                                |
                           [UFW:5432] -> [Docker] -> [postgres:5432]
                                |  
                           [UFW:6379] -> [Docker] -> [redis:6379]
```

### Scenario 3: Service Migration
When migrating from host-based to Docker-based services:
1. Preserve existing UFW rules
2. Add Docker published port rules
3. Remove old host service rules (tagged)
4. Maintain service availability throughout

## Testing Strategy

1. **Fresh Install Test**: Clean server, no UFW
2. **Existing UFW Test**: Server with UFW enabled and rules
3. **Docker Coexistence Test**: Docker + UFW together
4. **Re-run Safety Test**: Multiple security playbook runs
5. **Service Addition Test**: Adding services to secured server

## Rollback Plan

If issues arise:
1. UFW rules are backed up before changes
2. Can disable UFW temporarily: `ufw --force disable`
3. Restore from backup: `ufw --force reset && restore_rules.sh`
4. Docker iptables remain independent

## Future Enhancements

1. **UFW Rule Templates**: Predefined security profiles
2. **Geo-IP Blocking**: Country-based access control
3. **Rate Limiting**: Built-in DDoS protection
4. **Monitoring Integration**: Alert on rule changes
5. **Audit Logging**: Track all firewall modifications