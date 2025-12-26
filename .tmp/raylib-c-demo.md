# Spec: raylib-c-demo

## Meta

- Type: app
- Status: draft
- Tags: c, raylib, graphics, demo
- Description: Create a minimal C Raylib application that lives alongside the existing Python projects in this repo.

## Problem

- **context**: Repository currently lacks a native Raylib example even though we want to experiment with lightweight C graphics alongside the Python snake project.
- **goal**: Provide a small, well-structured Raylib demo that can act as a template for future C experiments.
## Requirements

- **Window & game loop** (critical)
  - Initialize Raylib, open an 800x450 window, and run a fixed-step loop until the user closes the window or presses ESC.
    - Window title should reference the repository (e.g., 'jk Raylib Demo').
    - Cap FPS to 60 using SetTargetFPS.
    - Cleanly close Raylib on exit.
- **Simple interactive visual** (high)
  - Draw at least one animated or interactive element to prove rendering + input works.
    - Include background clear color distinct from existing projects (e.g., dark purple).
    - Render a moving shape (circle or square) controlled by arrow keys.
    - Display on-screen text showing FPS and control hint.
- **Build integration** (medium)
  - Document build & run instructions and provide helper script(s) so repo contributors can compile easily on Linux/macOS.
    - Add a dedicated directory (e.g., raylib-demo/) with main.c and CMakeLists.txt or standalone Makefile.
    - Include README snippet or IMPLEMENTATION_REPORT entry describing dependencies (raylib >= 5.0).
    - Optional: fetch Raylib via git submodule or expect system install—decision should be noted.
## Implementation

- **approach**: Create a self-contained Raylib sample under raylib-demo/ that mirrors the repo's clean architecture expectations.
- **components**: 
  - 
    - **name**: Project layout
    - **details**: 
      - raylib-demo/main.c: entry point and game loop
      - raylib-demo/build.sh: convenience script invoking gcc or clang
      - raylib-demo/README.md: quick start instructions
  - 
    - **name**: Input & movement
    - **details**: 
      - Track a Vector2 position that updates when arrow keys are pressed
      - Clamp movement so demo shape stays on screen
  - 
    - **name**: Rendering
    - **details**: 
      - Clear background each frame
      - Draw moving shape plus FPS text via DrawText
      - Optional gradient or helper grid for extra flair
- **modified_files**: 
  - raylib-demo/main.c
  - raylib-demo/build.sh
  - raylib-demo/README.md
  - IMPLEMENTATION_REPORT.md (add Raylib section)
  - README.md (reference new demo)
## Testing

- **manual**: 
  - Build succeeds via build.sh on Linux with raylib installed
  - Window opens, shows animated/movable shape
  - Closing window or pressing ESC exits without errors
- **future_automation**: Consider adding a CI job that compiles the Raylib sample in headless mode once repo automation supports native builds.
## Tasks

- [ ] Scaffold raylib-demo/ directory: Create folder structure, helper scripts, and documentation
- [ ] Implement demo loop: Write Raylib C code with movement + drawing
- [ ] Document build steps: Explain dependencies and platform notes in README/IMPLEMENTATION_REPORT
## Notes

- Keep code minimal but idiomatic to Raylib
- Prefer zero external dependencies beyond Raylib standard distribution

