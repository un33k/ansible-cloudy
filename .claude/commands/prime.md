---
allowed-tools: Bash, Read  
description: Analyze codebase structure and README to load context for a new agent session  
---

# Prime

Load essential context for a new agent session by examining the codebase structure and README.

## Instructions

- Run `git ls-files` to map codebase structure and file organization  
- Read `README.md` to capture project purpose, setup, and key details  
- Output a concise project overview based on the above

## Context Sources

- **Codebase structure (git):** `!git ls-files`  
- **Codebase structure (tree):** `!eza . --tree`  
- **Primary README:** `@README.md`  
- **Additional docs:**  
  - `@CLAUD.md`  
  - `@.vault/README.md`  
  - `docs/**/*.md`
