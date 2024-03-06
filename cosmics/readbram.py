import time
import sys
import numpy as np

from argparse import ArgumentParser

parser= ArgumentParser()
parser.add_argument("-s","--sleep",type=int,help="Sleeping time in seconds", default=60)
parser.add_argument("-o","--output",help="Clean output file", default="data.txt")
parser.add_argument("-x","--exclude",action='append',help="Exclude link,hyb", default=[]) ## link,hyb

args=parser.parse_args()

from datetime import datetime
out = open(args.output, "w")
out.write("### " + str(datetime.now()) + "\n") ## add info
out.write("###iread link hyb hex(whole) nstubs bx chip_id strip bend Z\n") ## write info for data reading

import uhal

class color:
    red="\033[01;31m"
    green = "\033[01;32m"
    yellow = "\033[01;33m"
    blue = "\033[01;34m"
    magenta = "\033[01;35m"
    cyan = "\033[01;36m"
    white = "\033[01;30m" ## actually black
    reset = "\033[00m"



hw = uhal.getDevice("board", "chtcp-2.0://localhost:10203?target=192.168.0.194:50001", "file://settings/address_tables/uDTC_OT_address_table.xml")


## REG1
bram_waddr = hw.getNode("fc7_daq_ctrl.bram_block_reg1_sel.bram_waddr")

## REG0
link_id = hw.getNode("fc7_daq_ctrl.bram_block_reg0_sel.link_id")
hyb_id = hw.getNode("fc7_daq_ctrl.bram_block_reg0_sel.hyb_id")
raddr = hw.getNode("fc7_daq_ctrl.bram_block_reg0_sel.raddr")
whole0 = hw.getNode("fc7_daq_ctrl.bram_block_reg0_sel.whole")


### REG2
whole = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.whole")
nstubs = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.nstubs")
bx = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.bx")
chip_id = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.chip_id")
strip = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.strip")
bend = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.bend")
Z = hw.getNode("fc7_daq_ctrl.bram_block_reg2_sel.Z")

## REG3
reg3 = hw.getNode("fc7_daq_ctrl.bram_block_reg3_sel")
# enable bram
#reg3.write(0xffff0020)
# reset bram
#reg3.write(0xffff0030)
# start!
#reg3.write(0xffff0020)
#hw.dispatch()


rpntr = [[0 for i in range(2)] for j in range(2)]
#print(rpntr, file=sys.stderr)

iread = 0

# enable bram
reg3.write(0xffff0020)
hw.dispatch()
# reset bram
reg3.write(0xffff0030)
hw.dispatch()
# start!
reg3.write(0xffff0020)
hw.dispatch()

while True:
    iread+=1
    time.sleep(args.sleep)
    hw.dispatch()
    print("Reading", file=sys.stderr)
    
    for link in range(2):
        for hyb in range(2):
            if "%d,%d"%(link,hyb) in args.exclude: 
                print(color.yellow,"Ignoring",link,hyb,color.reset)
                continue

            ## DONT set maks values. They reset everything else. 

            word = np.uint32(0)
            word = np.bitwise_or( word ,  np.left_shift(link,24) )
            word = np.bitwise_or( word ,  np.left_shift(hyb,16) )
            word = np.bitwise_or( word ,  rpntr[link][hyb]  )

            print ("-> Writing word to reg0: ", hex(word))
            whole0.write(word)

            hw.dispatch()

            link_r = link_id.read()
            hyb_r = hyb_id.read()
            hw.dispatch()
            #print("--> L ",link_r, "H",hyb_r)

            waddr = bram_waddr.read()
            hw.dispatch()
            print(color.green + "Reading", "link", link, "hyb", hyb,color.reset, "waddr", waddr, "rpntr", rpntr[link][hyb], file=sys.stderr)

            while rpntr[link][hyb] != waddr: ### TODO: check offset by one when reading
                rpntr[link][hyb] += 1
                rpntr[link][hyb] %= 256

                word = np.uint32(0)
                word = np.bitwise_or( word ,  np.left_shift(link,24) )
                word = np.bitwise_or( word ,  np.left_shift(hyb,16) )
                word = np.bitwise_or( word ,  rpntr[link][hyb]  )

                whole0.write(word)
                
                hw.dispatch()
                
                whole_r = whole.read()
                nstubs_r = nstubs.read()
                bx_r = bx.read()
                chip_id_r = chip_id.read()
                strip_r = strip.read()
                bend_r = bend.read()
                Z_r = Z.read()
                hw.dispatch()

                print(iread, link, hyb, hex(whole_r), nstubs_r, bx_r, chip_id_r, strip_r, bend_r, Z_r)
                #### Write output file
                print(iread, link, hyb, hex(whole_r), nstubs_r, bx_r, chip_id_r, strip_r, bend_r, Z_r, file=out)

            sys.stdout.flush()
            sys.stderr.flush()
            out.flush()
            


