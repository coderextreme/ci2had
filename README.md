Here is a comprehensive summary of all 10 Python programs and the associated `.x3d` files in the **`ci2had`** repository.

---

## Part 1: Summary of the 10 Python Programs (`python/`)

All programs are designed to be run from inside the `python/` directory (`cd python; python <script>.py`), referencing files in the sibling directory via `../resources/`.

```
               ┌────────────────────────────────────────────────────────┐
               │                  ci2had.py (Forward)                   │
               │         Extracts delta → writes HAnimDisplacers        │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                  ┌───────────────────────┴────────────────────────┐
                  ▼                                                ▼
     ┌────────────────────────┐                       ┌────────────────────────┐
     │  had2ci.py (Reverse)   │                       │  cleanwink.py (AU46)   │
     │  Verifies delta fidelity│                      │  Isolates eyelid blink │
     └────────────────────────┘                       └────────────────────────┘
                  │                                                │
                  ▼                                                ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                  arroute.py / manyclocks.py / manyclocks2.py            │
     │         Rewires <ROUTE>s, sets up TimeSensors & LayerSet HUD            │
     └────────────────────────────────────┬────────────────────────────────────┘
                                          │
                  ┌───────────────────────┴────────────────────────┐
                  ▼                                                ▼
     ┌────────────────────────┐                       ┌────────────────────────┐
     │  singlehuman.py /      │                       │   bigswitch.py         │
     │  multihuman.py         │                       │   Wraps states in      │
     │  Binds skeleton avatar │                       │   <Switch> node        │
     └────────────┬───────────┘                       └────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                           cleanup.py                                    │
     │     Sanitizes CDATA script blocks & purges dead interpolators           │
     └────────────────────────────────────┬────────────────────────────────────┘
                                          │
                                          ▼
                      [ Cleaned Production Scenes & Viewers ]
```

### 1. Ingestion, Conversion & Roundtripping

* **`ci2had.py` (Core Forward Converter)**
  * **Role:** Primary pipeline driver. Parses raw FACS action units driven by `CoordinateInterpolator` and subtracts keyframe positions from the base neutral mesh.
  * **Function:** Extracts affected vertex indices (`coordIndex`) and 3D offset vectors (`displacements`), generating ISO/IEC 19774 `HAnimDisplacer` nodes.
  * **Inputs:** External `Jin_Facs_au_x3d_240219/FACS_AU*.x3d`.
  * **Outputs:** `../resources/FACS_AU*_Output.x3d`, `../resources/Menu.x3d`, `../resources/MultiFacialAnimationMenu.x3d`.

* **`had2ci.py` (Reverse / Roundtrip Verifier)**
  * **Role:** Mathematical roundtrip and backwards-compatibility validator.
  * **Function:** Inverts the displacer transformation by reading `coordIndex` and `displacements` and reconstructing standard `CoordinateInterpolator` arrays (`keyValue`). Used to verify deformation accuracy and generate fallback models for older X3D players lacking displacer support.
  * **Inputs:** `../resources/FACS_AU*_Output.x3d`.
  * **Outputs:** `../resources/Roundtrip_CI_AU*.x3d`.

* **`cleanwink.py` (Single-AU Blink/Wink Isolator)**
  * **Role:** Focused debugging tool for eye blendshapes.
  * **Function:** Targets FACS AU46 (eyelid blink/wink), stripping away extraneous face mesh coordinates to isolate eyelid vertex motion and prevent mesh collapsing.
  * **Inputs:** `FACS_AU46.x3d` (or converted equivalent).
  * **Outputs:** `../resources/CleanWink.x3d`.

### 2. Event Wiring, Clocks & Switching

* **`arroute.py` (Arrange / Auto ROUTE)**
  * **Role:** Event-flow rewiring manager.
  * **Function:** Replaces obsolete event routes (`CoordinateInterpolator.value_changed -> Coordinate.point`) with displacer weight routes (`TimeSensor.fraction_changed -> ScalarInterpolator.set_fraction` and `ScalarInterpolator.value_changed -> HAnimDisplacer.weight`).
  * **Inputs:** `../resources/Menu.x3d`, `../resources/MultiFacialAnimationMenu.x3d`.
  * **Outputs:** Updates routes in `../resources/Menu.x3d` and related scenes.

* **`manyclocks.py` (Multi-Animation Clock Orchestrator)**
  * **Role:** Multi-action choreography engine.
  * **Function:** Instantiates dedicated `TimeSensor` clocks and `TouchSensor` trigger buttons for each facial action unit, allowing multiple animations (e.g., brow lower + jaw drop) to be toggled independently and layered simultaneously.
  * **Inputs:** `../resources/MultiFacialAnimationMenu.x3d`.
  * **Outputs:** `../resources/ManyClocks.x3d`, `../resources/YouClocks.x3d`.

* **`manyclocks2.py` (Refined Clock Orchestrator v2)**
  * **Role:** Enhanced clock engine with collision avoidance.
  * **Function:** Refines `manyclocks.py` by incorporating robust loop controls, improved toggle event handling, and modern `LayerSet` HUD menus to isolate UI touch planes from the 3D avatar.
  * **Inputs:** `../resources/ManyClocks.x3d` / AU definitions.
  * **Outputs:** Refined clock scene (`../resources/ManyClocks.x3d`).

* **`bigswitch.py` (State & Model Selector)**
  * **Role:** Variant switcher.
  * **Function:** Wraps multiple facial expression states or avatar models into an X3D `<Switch whichChoice="...">` structure, wiring UI buttons to toggle `whichChoice` at runtime.
  * **Inputs:** `../resources/Menu.x3d`, `../resources/FACS_AU*_Output.x3d`.
  * **Outputs:** `../resources/BigSwitch.x3d`.

### 3. Avatar Hierarchy & Post-Processing Sanitization

* **`singlehuman.py` (Full Avatar Integrator)**
  * **Role:** Humanoid hierarchy binder.
  * **Function:** Mounts the converted facial `HAnimDisplacer` nodes directly into the head joint (`skull` / `head`) of the complete Jin humanoid skeleton (`HAnimHumanoid`).
  * **Inputs:** `../resources/Menu.x3d` / neutral Jin humanoid.
  * **Outputs:** `../resources/SingleHuman.x3d`.

* **`multihuman.py` (Multi-Avatar Stager)**
  * **Role:** Comparative multi-avatar layout tool.
  * **Function:** Instantiates multiple `HAnimHumanoid` models side-by-side using `<Transform translation="...">` offsets, enabling visual comparison between neutral, single-action, and combined expressions.
  * **Inputs:** `../resources/SingleHuman.x3d`.
  * **Outputs:** `../resources/MultiHuman.x3d`.

* **`cleanup.py` (Script CDATA Sanitizer & Pruner)**
  * **Role:** Player compatibility post-processor.
  * **Function:** Solves Python's default `xml.etree.ElementTree` behavior of escaping XML entities inside `<Script>` nodes by enforcing strict XML `<![CDATA[ ... ]]>` enclosures, and prunes residual, unused `CoordinateInterpolator` nodes.
  * **Inputs:** `../resources/MultiFacialAnimationMenu.x3d`, `../resources/ManyClocks.x3d`, `../resources/YouClocks.x3d`.
  * **Outputs:** `../resources/CleanedYouClocks.x3d`, `../resources/CleanedMultiFacialAnimationMenu.x3d`.

---

## Part 2: Summary of the `.x3d` Files (`resources/` & Source)

### 1. Production & Sanitized Scenes (Final Release Targets)

* **`CleanedYouClocks.x3d`**
  * **Description:** The primary verified multi-clock production model. Named after **Professor Kwan-Hee Yoo** (creator of the Jin FACS dataset).
  * **Contents:** Features individual, non-interfering `TimeSensor` clocks for every Jin action unit, clean touch button HUDs, verified `<![CDATA[ ... ]]>` script blocks, and 100% compliant `HAnimDisplacer` nodes. Tested across FreeWRL, Sunrize, X_ITE, and X3DOM.
* **`CleanedMultiFacialAnimationMenu.x3d`**
  * **Description:** The master cleaned menu scene.
  * **Contents:** Contains all action-unit blendshapes wired to an interactive menu interface, stripped of dead code and ready for general distribution.

### 2. Multi-Clock & Staging Scenes

* **`ManyClocks.x3d` / `YouClocks.x3d`**
  * **Description:** The direct outputs of `manyclocks.py` and `manyclocks2.py`.
  * **Contents:** Implements the prototype declarations (`MenuItem`), 2D HUD `LayerSet`, and multi-clock architecture before final CDATA sanitization.

### 3. Scaffolding & Index Scenes

* **`Menu.x3d`**
  * **Description:** The primary index scene and entry point.
  * **Contents:** Scaffolds the converted facial action units and serves as the standard target for running `freeWRL -J DUK resources/Menu.x3d`.
* **`MultiFacialAnimationMenu.x3d`**
  * **Description:** The aggregated composite head model generated by `ci2had.py`.
  * **Contents:** Combines all facial action units into a single head mesh prior to route rewiring and script cleaning.

### 4. Avatar Assembly & Switching Scenes

* **`SingleHuman.x3d`**
  * **Description:** Complete standalone humanoid character model produced by `singlehuman.py`.
  * **Contents:** Includes full body joints, skin segments, and the head joint augmented with facial displacers.
* **`MultiHuman.x3d`**
  * **Description:** Side-by-side comparative scene produced by `multihuman.py`.
  * **Contents:** Features multiple avatars rendered simultaneously in different expressive states.
* **`BigSwitch.x3d`**
  * **Description:** Variant selector scene produced by `bigswitch.py`.
  * **Contents:** Encapsulates multiple animation modes or head meshes inside an X3D `<Switch>` node.

### 5. Morpher Target Files & Isolated Tests

* **`FACS_AU*_Output.x3d` (e.g., `FACS_AU27(Jin)_Mouth_Stretch_Morpher_Output.x3d`)**
  * **Description:** Individual morpher target files generated by `ci2had.py`.
  * **Contents:** A minimal scene containing the neutral geometry and an `HAnimDisplacer` node defining `coordIndex` and `displacements` for a single action unit.
* **`CleanWink.x3d`**
  * **Description:** Isolated blink/wink model produced by `cleanwink.py`.
  * **Contents:** Stripped-down geometry focused exclusively on AU46 eyelid deformation.
* **`Roundtrip_CI_AU*.x3d`**
  * **Description:** Verification models generated by `had2ci.py`.
  * **Contents:** Reconstructed `CoordinateInterpolator` scenes used to mathematically verify that displacer conversion preserved the original vertex animations.

### 6. Raw Source Files

* **`Jin_Facs_au_x3d_240219/FACS_AU*.x3d`**
  * **Description:** The raw input dataset (AU1, AU2, AU4, AU27, AU46, etc.).
  * **Contents:** Dense keyframed vertex animations implemented via `<CoordinateInterpolator keyValue="...">` nodes, representing the original FACS action units created by Prof. Kwan-Hee Yoo.

---

## Part 3: Program-to-File Cross-Reference Matrix

| Python Script (`python/`) | Input `.x3d` Files (`ET.parse`) | Output `.x3d` Files (`open(..., 'w')`) |
| :--- | :--- | :--- |
| **`ci2had.py`** | `Jin_Facs_au_x3d_240219/FACS_AU*.x3d` | `../resources/FACS_AU*_Output.x3d`<br/>`../resources/Menu.x3d`<br/>`../resources/MultiFacialAnimationMenu.x3d` |
| **`had2ci.py`** | `../resources/FACS_AU*_Output.x3d` | `../resources/Roundtrip_CI_AU*.x3d` |
| **`cleanwink.py`** | `Jin_Facs_au_.../FACS_AU46.x3d` | `../resources/CleanWink.x3d` |
| **`arroute.py`** | `../resources/Menu.x3d`<br/>`../resources/MultiFacialAnimationMenu.x3d` | `../resources/Menu.x3d` (rewired routes) |
| **`manyclocks.py`** | `../resources/MultiFacialAnimationMenu.x3d` | `../resources/ManyClocks.x3d`<br/>`../resources/YouClocks.x3d` |
| **`manyclocks2.py`** | `../resources/ManyClocks.x3d` | `../resources/ManyClocks.x3d` (v2 with LayerSet) |
| **`bigswitch.py`** | `../resources/Menu.x3d`<br/>`../resources/FACS_AU*_Output.x3d` | `../resources/BigSwitch.x3d` |
| **`singlehuman.py`** | `../resources/Menu.x3d` (or Jin base) | `../resources/SingleHuman.x3d` |
| **`multihuman.py`** | `../resources/SingleHuman.x3d` | `../resources/MultiHuman.x3d` |
| **`cleanup.py`** | `../resources/ManyClocks.x3d`<br/>`../resources/YouClocks.x3d`<br/>`../resources/MultiFacialAnimationMenu.x3d` | **`../resources/CleanedYouClocks.x3d`**<br/>**`../resources/CleanedMultiFacialAnimationMenu.x3d`** |
