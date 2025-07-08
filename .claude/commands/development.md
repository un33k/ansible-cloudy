# Ansible Cloudy Development Notes

## Version Status

- **Current version:** _(not yet released)_  
- **Backward compatibility:** Not a concern before v1.0 release

---

## Architecture Decisions

### Service Installation Pattern (Implemented)

We support two distinct installation modes:

1. **Service-only commands**  
2. **Full server commands**

---

### Special Cases

_[Document any exceptions or overrides here]_

---

### Rationale

This pattern improves clarity and flexibility:

- Clear user intent (service vs full server)  
- No surprises for advanced users  
- Safe defaults for new users  
- Clean separation of concerns
