import os
import subprocess

from amaranth.build import *
from amaranth.vendor import GowinPlatform

from .resources import *


__all__ = ["TangNano20kPlatform"]


class TangNano20kPlatform(GowinPlatform):
    part          = "GW2AR-LV18QN88C8/I7"
    family        = "GW2AR-18C"
    default_clk   = "sys_clk"
    osc_frequency = 27_000_000
    resources     = [
        Resource("sys_clk", 0, Pins("4", dir="i"),
                 Clock(27_000_000), Attrs(PULL_MODE="UP")),
        
        #MS5351M clock generator, controlled by I2C from MCU
        Resource("pll_clk0", 0, Pins("10", dir="i"), Attrs(PULL_MODE="UP")),
        Resource("pll_clk1", 0, Pins("11", dir="i"), Attrs(PULL_MODE="UP")),
        Resource("pll_clk2", 0, Pins("13", dir="i"), Attrs(PULL_MODE="UP")),

        # S1 S2 buttons
        *ButtonResources(pins="88 87", invert=True,
                         attrs=Attrs(PULL_MODE="UP")),

        # Led row
        *LEDResources(pins="15 16 17 18 19 20", invert=True,
                      attrs=Attrs(PULL_MODE="UP", DRIVE=8)),

        # UART connected to MCU
        UARTResource(0, rx="70", tx="69",
            attrs=Attrs(PULL_MODE="UP", IO_TYPE="LVCMOS33")),

        # 64 Mbit flash for FPGA bitstream
        *SPIFlashResources(0,
            cs_n="60", clk="59", copi="61", cipo="62",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        *SDCardResources(0,
            clk="83", cmd="82", dat0="84", dat1="85", dat2="80", dat3="81", wp_n="-",
            attrs=Attrs(IO_TYPE="LVCMOS33")),

        Resource("lcd", 0,
            Subsignal("clk", Pins("77", dir="o")),
            Subsignal("hs", Pins("25", dir="o")),
            Subsignal("vs", Pins("26", dir="o")),
            Subsignal("de", Pins("48", dir="o")),
            Subsignal("r", Pins("42 41 40 39 38", dir="o")),
            Subsignal("g", Pins("37 36 35 34 33 32", dir="o")),
            Subsignal("b", Pins("31 30 29 28 27", dir="o")),
            Attrs(IO_TYPE="LVCMOS33")),

        Resource("lcd_backlight", 0, Pins("49", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33")),

        Resource("hdmi", 0,
             Subsignal("clk", DiffPairs(p="33", n="34", dir="o")),
             Subsignal("d", DiffPairs(p="35 37 39", n="36 38 40", dir="o")),
             Attrs(PULL_MODE="NONE", DRIVE=8)),
        
        #WS2812 RGB led
        Resource("ws2812", 0, Pins("79", dir="o"),
                 Attrs(IO_TYPE="LVCMOS33")),
        
        # MAX98357AEWL+T
        Resource("audio_en", 0, Pins("51", dir="o"),
                 Attrs(PULL_MODE="NONE", DRIVE=8)), # SD_MODE / Enable
        Resource("audio_i2s", 0,
            Subsignal("clk", Pins("56", dir="o")), # BCLK
            Subsignal("din", Pins("54", dir="o")), # DIN
            Subsignal("ws", Pins("55", dir="o")), # LRCLK
            Attrs(PULL_MODE="UP", DRIVE=8)),

    ]
    connectors = []

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = {
            "add_options":
                "set_option -use_mspi_as_gpio 1 -use_sspi_as_gpio 1",
            "gowin_pack_opts":
                "--sspi_as_gpio --mspi_as_gpio"
        }
        return super().toolchain_prepare(fragment, name, **overrides, **kwargs)

    def toolchain_program(self, products, name):
        with products.extract("{}.fs".format(name)) as bitstream_filename:
            subprocess.check_call(["openFPGALoader", "-b", "tangnano20k", bitstream_filename])


if __name__ == "__main__":
    from .test.blinky import *
    TangNano20kPlatform().build(Blinky(), do_program=True)
