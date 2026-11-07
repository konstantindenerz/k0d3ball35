# Lessons from the Keyball39 and its relatives

What the holykeebs Keyball39 (the board this project replaces on the user's desk) and
other trackball splits do well, where they fall short, and what k0d3ball35 does about it.
Every item cites its source. Sources are build logs, long-term reviews, GitHub discussions
and vendor docs; "k0d3ball35 response" refers to decisions in `docs/01-design-spec.md`.

## 1. The holykeebs Keyball39

holykeebs (a small shop in Israel) sells the Keyball39/44/61/61+ in partnership with
Yowkees (Shirogane Lab). Their documentation lives at
[docs.holykeebs.com](https://docs.holykeebs.com/guides/keyboard/keyball/) (source repo
[holykeebs/docs](https://github.com/holykeebs/docs)); the firmware in
[holykeebs/qmk_firmware](https://github.com/holykeebs/qmk_firmware/tree/hk-master/keyboards/holykeebs)
(hk-master, VIA), [holykeebs/vial-qmk](https://github.com/holykeebs/vial-qmk) (hk-master, Vial)
and the shared userspace [holykeebs/qmk-userspace](https://github.com/holykeebs/qmk-userspace),
with precompiled images in [holykeebs/qmk_compiled](https://github.com/holykeebs/qmk_compiled/releases/tag/latest).
Licences: the QMK forks are GPL-2.0, the userspace and docs repos carry no licence file.

### 1.1 What holykeebs changed versus the Yowkees kit

| Area | Yowkees / Yushakobo kit | holykeebs | Source |
|---|---|---|---|
| PCB | green/white | black, "the rest is identical" | [guide](https://docs.holykeebs.com/guides/keyboard/keyball/) |
| Plates, screws | 2 mm / 3 mm acrylic, M2 | different plate thicknesses and M2 screws | guide |
| Controller | Pro Micro (ATmega32U4) or RP2040 Pro Micro | RP2040 only (Sea-Picro / RP2040 Pro Micro), "ample storage so firmware size is not an issue" | guide, [firmware](https://docs.holykeebs.com/firmware/) |
| Sockets | 12-pin conthrough or pin headers | optional custom low-profile headers, PCB-to-controller height 5 mm, "less prone to bending" | [buyers guide](https://docs.holykeebs.com/guides/buyers-guide/) |
| Trackball | 34 mm, not included | 34 mm, not included, Perixx PERIPRO-303 recommended | guide |
| Ball housing | injection moulded, 3 ceramic bearings | same stock housing; separate "Keyball Trackball Case" product in black resin with ceramic bearings because "the ball pops out when swiping up and down" with the stock holder | [product](https://holykeebs.com/products/keyball-trackball-case) |
| Thumb keys | 5 MX/Choc hybrid positions | Choc hot-swap sockets always included for the thumb cluster | guide |
| Firmware | Yowkees QMK out-of-tree keyboard, Remap/Keyball Link | holykeebs userspace, QMK's native PMW3360 driver, RGB Matrix, `HK_*` keycodes, Vial/VIA; one image for all ball configurations, ball side detected at boot | guide, firmware page |
| Keyball61+ | n.a. | holykeebs-only variant with clickable horizontal encoders per half ("remove the need for drag scrolling") and a lily58-style keymap | guide |

The holykeebs Keyball39 keyboard definition keeps Yowkees' electrical design: 4x6 matrix
per half on GP29/28/27/26 rows and GP4..GP9 columns, COL2ROW, hand detection through a
matrix grid cell, PMW3360 on SPI0, one WS2812 chain per half, USB VID 0xC3AC / PID 0x3142
([config.h](https://raw.githubusercontent.com/holykeebs/qmk_firmware/hk-master/keyboards/holykeebs/keyball39/config.h),
[keyboard.json](https://raw.githubusercontent.com/holykeebs/qmk_firmware/hk-master/keyboards/holykeebs/keyball39/keyboard.json)).
The two warnings in their guide are worth copying verbatim into any trackball-split
documentation: "Avoid connecting / disconnecting the TRRS cable when the keyboard is
powered. This can short the GPIO pins of the controllers." and (trackball module guide)
"Make sure solder has actually gone through to the controller pins under the shield".

### 1.2 holykeebs firmware features worth matching

From [users/holykeebs/holykeebs.h](https://github.com/holykeebs/qmk-userspace/blob/hk-master/users/holykeebs/holykeebs.h)
and the [firmware page](https://docs.holykeebs.com/firmware/#features):

| Feature | holykeebs keycode / behaviour | k0d3ball35 (ZMK) equivalent |
|---|---|---|
| Two sensitivity profiles, default and sniping; on the PMW3360 realised as hardware CPI | `HK_P_SET_D`, `HK_P_SET_S` (hold, then +/-), `HK_S_MODE`, `HK_S_MODE_T` | `res-cpi` 400 default plus snipe layer 6 with `zip_xy_scaler 1 3`; no runtime CPI keys yet (ticket below) |
| Drag scroll (moves become scroll) | `HK_D_MODE`, `HK_D_MODE_T` | scroll layer 5 (`zip_xy_to_scroll_mapper`) |
| Scroll throttle ("how much ball travel maps to one unit of scroll") | `HK_P_SET_THR` | `zip_scroll_scaler 1 6`; not adjustable at runtime |
| Scroll lock (vertical / horizontal only), invert scroll | `HK_C_SCROLL`, `HK_I_SCROLL` | not implemented (ticket: scroll axis lock, Keyball "scroll snap") |
| Auto mouse layer with runtime toggle and timeout +/- 50 ms, saved to EEPROM | `HK_AML_T`, `HK_AML_UP`, `HK_AML_DN`, `HK_SAVE` | `zip_temp_layer 4 700` with `require-prior-idle-ms 150`; fixed at build time |
| Settings persist only on explicit save | `HK_SAVE`, `HK_RESET`, `HK_DUMP` | ZMK Studio stores keymap changes; pointer settings are compile-time |
| Peripheral-side control: hold Shift with any `HK_` key to target the other half | convention | n.a. (single sensor) |
| Hires scrolling, 1 unit per wheel notch | `POINTING_DEVICE_HIRES_SCROLL_ENABLE` | ZMK smooth scrolling in `k0d3ball35.conf` |
| Encoders as scroll (61+) | `HK_ENC_SCR_U/D` | out of scope (no encoder) |
| OLED info panels and bongocat | `HK_BONGO_T` | no display by design |

Keycodes start at `QK_KB_0` (0x7E00) in the same numbering style as Yowkees' `KBC_*`
keycodes, so Vial users see them by name. The Keyball default keymap convention that
holykeebs keeps: a settings layer on the left inner thumb that also puts the ball into
scroll mode. k0d3ball35's keymap follows the same convention (hold thumb = scroll).

### 1.3 Things to stay compatible with

- Ball: 34 mm Perixx is the holykeebs default; our 19 mm choice is a deliberate break (see 3.3).
- Keymap habits: scroll on a held thumb key, sniping on a held key, auto mouse layer with a
  timeout around 500 to 700 ms, mouse buttons on the left-hand home row. Our ZMK keymap
  mirrors this so switching between the two boards costs nothing.
- Configuration tool: holykeebs uses Vial, Yowkees uses Remap. Neither speaks to ZMK; see
  ticket `fw-remap-compatibility` (Remap works with BLE Micro Pro or an RP2040 Pro Micro
  running QMK, both of which fit our Pro Micro footprint).
- Low-profile headers: with the cell under the PCB instead of under the controller, the lowest
  sockets (Mill-Max 315, conthrough) are the match; holykeebs' 5 mm headers were for the
  arrangement; mill-max 1.27 mm strips are the fallback.

## 2. Weaknesses reported by Keyball users

### 2.1 Ergonomics

| # | Weakness | Source | k0d3ball35 response |
|---|---|---|---|
| E1 | Left pinky pain after about a month: the key entry angle for the outer column is oblique and loads the second joint. "No perfect solution"; tenting and lighter switches help. | [naenote review](https://www.naenote.net/entry/keyball-39-review) | Column stagger kept (it is the Keyball's strength), 18x17 Choc pitch shortens pinky travel by 1 mm per row; tenting is a case-phase topic (`mech-case`). Recommend 20 g to 25 g Choc springs for the pinky column in the build guide. |
| E2 | Thumb cluster on the 39 sits closer than on the 44, so a horizontal ball swipe hits the thumb keys. | naenote | Since r2.3 the right half has only the two INNER thumb keys and the 19 mm ball sits where the outer one was, 29.5 mm from the middle thumb centre with a 28 mm clearance circle and 1 mm minimum keycap clearance enforced by `check_layout`. Keyball 39/44/61 sacrifice the same key; reading their KiCad sources is what corrected our first attempt, which dropped the inner key instead and left the ball under the ring column. |
| E3 | Thumb arc feels loose; the innermost thumb key (next to the controller) should sit further forward. Thumb spring too stiff. | [goropikari build log](https://goropikari.hatenablog.com/entry/keyball39_build_log) | Arc geometry copied from the Keyball (0/10/20 deg, 19.5 mm pitch) but with only 3 keys the innermost one is the Keyball's "thumb 3", which that author wanted forward. Ticket candidate: thumb arc offset parameter in the layout yaml for a test print. |
| E4 | Keys "below C" and "below X" (row 4 under the finger columns) need hand movement; the reviewer never uses them. | [naenote Keyball44](https://www.naenote.net/entry/keyball-44-review) | Those positions do not exist on k0d3ball35 (35 keys). Accepted. |
| E5 | With low-profile caps the palm touches the 34 mm ball while typing and the auto mouse layer fires by accident. | [rriver journey](https://note.com/rriver/n/n7ee97b12c473), [akkagi on 25 mm](https://x.com/akkagi0416/status/1731677056092475430), [search summary](https://note.com/hundert_phigik/n/na6b844909f82) | Main reason for a small ball. r1's 25 mm ball still stood 23 mm above the PCB because the PMW3610 sits straight below it; r2 goes to 19.05 mm (ball top 17 mm, 6 mm above the caps, the torabo-tsuki LP 19 mm precedent) and puts the ball in a case pocket beside the PCB (`mech-ball-height-23mm`). The auto mouse layer has `require-prior-idle-ms 150` and a movement threshold; `fw-cpi-tuning-19mm` covers the threshold. |
| E6 | Scrolling needs two hands (hold layer key + roll). Reviewer kept a separate mouse for photo work. | [insnote 1-year review](https://insnote.net/keyball39_longterm-review/) | Scroll layer on a right-hand thumb key so one hand can scroll; a toggle variant (like `HK_D_MODE_T`) is a keymap change. Ticket candidate: one-handed scroll toggle. |
| E7 | Learning curve of 39 keys and layers, 1.5 months; tap-hold misfires; not beginner friendly; no warranty. | naenote, [base-g](https://base-g.com/keyball39-3-month-review/), [sensai-gadget](https://sensai-gadget.com/separate-keyboard-to-normal-keyboard-reason/) | Inherent to the class. ZMK Studio removes the compile-edit-flash loop; the build guide must say that the first week is slow. |

### 2.2 Trackball mechanics

| # | Weakness | Source | k0d3ball35 response |
|---|---|---|---|
| T1 | Stock Keyball holder: the ball pops out when swiping up/down; holykeebs sells a resin replacement case for exactly this. | [holykeebs trackball case](https://holykeebs.com/products/keyball-trackball-case), Charybdis "without tenting the trackball can pop out while scrolling" ([bastardkb reviews](https://bastardkb.com/product/charybdis-nano-kit/)) | Accepted on the desk: the ball sits 1.95 mm deep in the pocket below the PCB on three bearings 35 degrees under the equator and is not flicked out by normal swipes; no retainer by design so the thumb reaches the equator from every side. In transport the removable case lid keeps it in (`mech-case-lid`). Must be test-printed; see `mech-trackball-cradle`. |
| T2 | Ceramic bearings fall off the stock housing; the kit ships a spare and tells you to glue it. | [Yowkees build guide](https://github.com/Yowkees/keyball/blob/main/keyball39/doc/rev1/buildguide_en.md), [search summary](https://github.com/Yowkees/keyball/discussions/687) | Cradle seats are press-fit with slight undersize plus a glue pocket; spare balls in the BOM. |
| T3 | Stiction and crunch from dust on static ceramic bearings; several owners switched to roller-bearing or ball-transfer-unit ("ball slider") cases: smoother, but roller cases are hard to assemble in PLA (tap screws strip, soldering-iron workaround) and BTU cases add about 4 mm height and grip the ball tightly. | [electrical_cat bearing case](https://note.com/electrical_cat/n/n30146519df5f), [hyakum ball-slider case](https://note.com/hundert_phigik/n/na7fc7492c91a), [kbd.news bearing comparison](https://kbd.news/Trackball-bearing-comparison-1757.html) | Static ZrO2 balls kept: the kbd.news test rates them best for consistency and silence, BTUs gritty at low speed, rollers "awful" for direction dependence. Accepted trade-off; cleaning procedure in the build guide. A BTU variant of the cradle is a possible later option (ticket candidate). |
| T4 | Small balls are picky: semi-transparent stone balls barely track, some POM/plastic balls give erratic cursor paths, a resin billiard ball tracked best; "white, yellow and black resin balls do not move the cursor" with the stock sensor, stainless works but is heavy. | [hyakum 25 mm ball test](https://note.com/hundert_phigik/n/na6b844909f82), [rshosai](https://x.com/rshosai/status/1754699345340101013), [torabo-tsuki ball pickiness](https://note.com/sasanokino/n/nfa1a93fe67da) | The 19.05 mm POM ball is what torabo-tsuki LP ships and what its seven-month review tracked without problems; the BOM adds the PandaKB TB19 phenolic ball as the premium option. `hw-19mm-ball-sourcing` asks to test balls from the pack before the PCB order. Avoid glossy white and translucent balls. |
| T5 | 25 mm on a board designed for 34 mm: cursor needs more rotation per pixel, the thumb travels further from ball to thumb keys, the sensor board height is the real bottleneck; one author reverted to 34 mm. | [allium downsizing report](https://note.com/alliumtuberosum/n/nc146aa1936d2) | Layout is designed around the small ball from the start (ball centre 5 mm outboard of the index column, in the outer thumb key's former place). CPI 600 default and tuning ticket `fw-cpi-tuning-19mm`. The sensor board height was attacked by taking it off the PCB entirely: it lies on the case floor in the pocket (`mech-ball-height-23mm`). |
| T6 | Ball housing height warps thin printed covers; the universal-PCB wireless mod made the right half too tall for a soft case. | [hyakum wireless summary](https://note.com/hundert_phigik/n/n1a9e137b5e09) | Case phase gets a 32 mm pocket with the cradle screwed to the floor instead of a dome over a PCB-mounted module; the ball top is 17 mm above the PCB, 6 mm above the caps (`mech-case-ball-pocket`). |

### 2.3 Electrical and build

| # | Weakness | Source | k0d3ball35 response |
|---|---|---|---|
| B1 | TRRS hot-plug destroys GPIO: a Keyball39 owner lost sync after re-plugging under power; Shirogane Lab confirmed it is a known failure and the Pro Micro had to be replaced (and PCB pads were damaged while desoldering). | [discussion #801](https://github.com/Yowkees/keyball/discussions/801), [gabevenberg on TRRS](https://gabevenberg.com/posts/stop-using-trrs/), holykeebs warning | No TRRS at all (BLE split). The controller sits in sockets so it can be swapped without desoldering. |
| B2 | PMW3360 needs 1.9 V core and 5 V-tolerant level shifting; the daughterboard is the hardest soldering (invisible cold joint on sensor pin 8 killed the trackball; "purple Pro Micro" voltage doubts). | [discussion #144](https://github.com/Yowkees/keyball/discussions/144), Keyball46 sensor gerbers | PMW3610 runs VDDIO at 3.3 V without shifters; our sensor board has test points on every signal so a cold joint can be found with a meter. |
| B3 | PMW3360 draws about 23 mA: with BLE Micro Pro the ball half lasted 9 to 12 h on 930 mAh while the plain half did 60 h on 650 mAh. | [hyakum wireless summary](https://note.com/hundert_phigik/n/n1a9e137b5e09) | PMW3610 at 0.6 mA tracking / 36 uA rest; that alone is the reason k0d3ball35 is not a BMP conversion. Measurement ticket `fw-battery-drain-measurement`. |
| B4 | Keyboard not recognised on MacBook for minutes; both OLEDs show the logo. Cause: `SPLIT_USB_TIMEOUT` too short. | goropikari | Not applicable (BLE split, right half central). USB-only mode is still a ZMK option. |
| B5 | Switch plate holes too tight for Kailh switches, hours of filing; middle plate and OLED rattle, fixed with tape; case flexes, rubber feet uneven; TRRS jack sits at the edge of the case opening. | goropikari, naenote Keyball44, [search summary](https://goropikari.hatenablog.com/entry/keyball39_build_log) | No plate (Choc hot-swap on the PCB), no OLED, no TRRS. Case phase: foot positions on the 5 mounting holes per half, not the plate. |
| B6 | Eight solder jumpers for the sensor lines plus four OLED jumpers plus a hand jumper; easy to miss one. | Yowkees build guide chapter 3/5 | No jumpers at all since r2: two separate PCBs with identical controller wiring, no hand jumper (ZMK builds per side). r1's reversible board still needed three power-row jumpers, which is one of the reasons it was dropped. |
| B7 | Pro Micro header pins bend when removed from sockets. | holykeebs buyers guide | Mill-Max 315 sockets with 3320 pins or conthrough spring pins; build guide. |

### 2.4 Firmware and feel

| # | Weakness | Source | k0d3ball35 response |
|---|---|---|---|
| F1 | Trackball scrolling imprecise, "often had to put up with it"; a reviewer went back to a normal keyboard partly for this and for wireless instability on torabo-tsuki. | sensai-gadget, sasanokino | Scroll via `zip_xy_to_scroll_mapper` with scaler 1/6 and ZMK smooth scrolling; needs on-hardware tuning (ticket). Axis lock (Keyball scroll snap) not yet implemented. |
| F2 | Auto mouse layer timing: too long gives stray text input, too short loses clicks; accidental activation from palm contact. | [aaron-powell](https://www.aaron-powell.com/posts/2026-09-10-upgrading-my-keyboard-with-a-trackball/), goropikari | `require-prior-idle-ms 150`, 700 ms timeout, mouse-button positions excluded from the layer timer. Runtime timeout keys like `HK_AML_UP/DN` would help; ticket candidate. |
| F3 | Default cursor speed too fast for fine work; CPI keys hidden (Remap showed only "custom keycode 27-30"). | aaron-powell, hyakum | Snipe layer plus documented keymap; runtime CPI step keys are a ticket candidate (ZMK has no built-in behaviour for `res-cpi` changes at runtime). |
| F4 | Firmware compile needed for CPI/tap-hold changes; scattered information for wireless conversions. | insnote, monograph video, hyakum | ZMK Studio for keymap, CI builds for firmware, one docs folder. |
| F5 | torabo-tsuki: peripheral half sometimes does not wake from sleep and needs a power cycle; keys next to the ball (N, M) hard to press. | sasanokino | ZMK sleep timeout 30 min and ext-power settings are in the conf; the wake issue is a known ZMK split topic, keep an eye on it after the first build (`fw-ball-motion-wake` is related). No key sits inside the cradle radius plus 1 mm. |
| F6 | PMW3610 with a white ball: no movement, orange ball works. | [PMW3610 search summary](https://www.tindie.com/products/randware/pmw3610-breakout-board/) | Same as T4: ball colour matters for the PMW3610 too; test before committing to a white ball for the photo look. |

## 3. Design decisions confirmed by the field reports

1. **No TRRS, no OLED, no plate** removes B1, B4, B5 and B6 entirely.
2. **PMW3610 at 3.3 V on a daughterboard with test points** answers B2 and B3; it is the single
   biggest reason the community moved from BMP conversions to ZMK boards.
3. **19 mm ball in a case pocket** fixes E5 for low-profile caps (ball top 6 mm above the caps
   instead of 12) but imports T4 and T5; both are mitigated (balls with a precedent, layout
   designed for the small ball, CPI 600) and the 25 mm cradle stays a fallback.
4. **Static ceramic bearings, no retainer, a transport lid** answer T2, accept T1 on the desk and close it in the bag, while accepting T3.
5. **Socketed controller, two plain PCBs without jumpers** answer B6 and B7.

## 4. Ticket candidates (prioritised)

| Name | Priority | One line |
|---|---|---|
| `fw-scroll-axis-lock` | P2 | Scroll snap / axis lock like Keyball `SSNP_*` and holykeebs `HK_C_SCROLL`, as a ZMK input processor or layer. |
| `fw-runtime-pointer-settings` | P2 | Runtime CPI step, sniping toggle, auto-mouse timeout +/- keys (holykeebs `HK_P_SET_*`, `HK_AML_UP/DN`) via ZMK behaviours or Studio. |
| `fw-one-handed-scroll-toggle` | P3 | Toggle variant of the scroll layer so scrolling does not need a held key (E6). |
| `mech-thumb-arc-tuning` | P2 | Expose the thumb arc offset/rotation in the layout yaml and test-print two variants (E3). |
| `mech-pinky-column-springs` | P3 | Recommend 20 to 25 g springs for the outer column in the build guide (E1). |
| `mech-cradle-btu-variant` | P3 | Optional ball-transfer-unit cradle for users who prefer lower stiction (T3). |
| `hw-ball-colour-tracking-test` | P1 | Test the two BOM balls (matte) and a white ball on the PMW3610 before ordering caps/ball in a colour (T4, F6). |
| `doc-keyball-owner-migration` | P3 | A page for Keyball39 owners: keymap mapping Keyball/holykeebs keycodes to our layers, what feels different (ball height, 19 mm). |
| `mech-case-ball-dome` | P2 | Case phase: plan the pocket rim and tenting so the ball top (+17 mm) does not force a tall flat cover (T6). |
| `fw-split-sleep-wake-check` | P2 | After first assembly, verify the peripheral wakes from deep sleep reliably (F5). |
