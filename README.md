# Pico Gameboy
I came across with this DIY Gameboy video made of Raspberry Pi Pico and inspired me to build my own version. The fact that RP2040 has dual-core ARM Cortex-M0+ processor makes it capable of running some light emulators. So I’ll build a little handheld game console using RP2040 that can run gameboy!

![demo](assets/demo.png)

# Features
- Full-on Gameboy experience: Actually runs the classics smoothly without freaking out.
- Insanely portable: Squeezed everything into a super compact custom PCB so you can just chuck it in your pocket.
- 100% Custom Hardware: Fully designed, routed, and reflowed by yours truly (my eyes are still bleeding from staring at KiCad traces bruh).

# Components
- RP2040
- 12MHz Crystal (ABM8-272-T3)
- 8MB Flash Storage (W25Q64JVXGIQ)
- Buck-Boost Switching Regulator (RT6150B)
- USB-C (TYPE-C-31-M-12)

# PCB Designs
- 2 layers
- Single-sided component placement
- 2.6mm board thickness
- HASL (with lead) surface finish
- 1oz outer copper weight

## PCB Schematic
![schemtatic](assets/schematic.svg)

## PCB Layouts
![pcb_front](assets/chess_card-B_Cu.svg)
![pcb_back](assets/chess_card-F_Cu.svg)
![pcb_design](assets/pcb.png)

## 3D Model
![3d_model_front](assets/3d_model_front.png)
![3d_model_back](assets/3d_model_back.png)

# How to order
- Download the zip file
- Upload the zip file to JLCPCB
- Select PCBA and continue
- Upload BOM.csv and position.csv
- Select the parts and submit payment
