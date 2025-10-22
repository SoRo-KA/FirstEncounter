# Pymirokai

**Pymirokai** is a modular Python library for interfacing with the Mirokai API, designed with access levels to ensure functionality tailored to specific user permissions. The library is distributed in two distinct packages:

- **Admin Level (`pymirokai[admin]`)**: Includes all functions available to admins and users.
- **User Level (`pymirokai[user]`)**: Provides basic functionality for general client use.

Each package is built to meet specific needs, and switching between them requires uninstalling the previous version before installing the desired one.

## Installation Guide

### Install Prebuilt Packages

To install a prebuilt wheel package:

1. **Choose the appropriate wheel file:**
   - Admin Level: `pymirokai_admin-x.x.x-py3-none-any.whl`
   - User Level: `pymirokai_user-x.x.x-py3-none-any.whl`

   Replace `x.x.x` with the package version.

2. **Install using pip:**
   ```bash
   python3 -m pip install ./path/to/whl/file.whl
   ```

---

## Key Features by Access Level

- **User Level (`pymirokai[user]`)**: General client features.
- **Admin Level (`pymirokai[admin]`)**: Advanced functionality, including all user-level features.

---

## Troubleshooting

1. **Incompatibility of Versions**:
   - Packages (`pymirokai[user]` and `pymirokai[admin]`) are not intercompatible. Uninstall the currently installed package before switching.
   ```bash
   python3 -m pip uninstall pymirokai_user pymirokai_admin
   ```

2. **Check Installed Version**:
   ```bash
   pip show pymirokai_user pymirokai_admin
   ```

---

This streamlined setup allows seamless interaction with the Mirokai API based on the desired functionality and access level. For detailed usage examples, consult the `Pymirokai Documentation`
