from argparse import ArgumentParser
parser=ArgumentParser()
parser.add_argument("-f","--file",help="input file",default="cosmics1.txt")
parser.add_argument("-o","--out",help="output file",default="processed/run1.csv")
### For ignoring the first read
parser.add_argument("--ignore_first",help="ignore first read (default)",default=False,action='store_true')
parser.add_argument("--do_first",help="do first read",dest='ignore_first',action='store_false')
### 
parser.add_argument("--run_offset_scan",help="run offset scan",default=True,action='store_true')
parser.add_argument("--no_offset_scan",help="run offset scan",dest='run_offset_scan',default=False,action='store_false')
###
args = parser.parse_args()
#args.ignore_first=True

from datetime import datetime
import re
import json
import numpy as np

def time_match(events, fout, verbose=False, window=1, offset = 0):
    matched= 0
    if verbose: 
        print("Processing events", len(events))
    closest=[]
    for l1, h1, bx1, chip1, strip1 ,bend1 ,z1 in events:
        cand = -1 ## closest candidate
        minDeltaBx = 2048
        for je, (l2, h2, bx2, chip2, strip2 ,bend2 ,z2) in enumerate(events):
            if l1 == l2: continue ## a muon event needs to be on different links / modules
            if abs(bx1-bx2)<minDeltaBx: 
                cand = je
                minDeltaBx = abs(bx1-bx2)
        closest.append(cand)

    if verbose: 
        for ie in range(0,len(events)):
                print("*",ie, events[ie], "->", closest[ie])
        print("---")

    for ie, (l1, h1, bx1, chip1, strip1 ,bend1 ,z1) in enumerate(events):
        if l1 != 0: continue ## make sure first link is 0
        if verbose: print("matching event",ie) 
        if closest[ie] <0 : continue ## no match
        if verbose: print(" > has a closest") 
        je = closest[ie]
        if closest[je] != ie: continue ## that guy has another better candidate
        if verbose: print(" > the other agrees") 
        l2, h2, bx2, chip2, strip2 ,bend2 ,z2 = events[je]
        if abs(bx1-bx2-offset) > window : continue
        if verbose: print(" > bx is within window") 
        
        closest[je] = -1 ## avoid duplicate processing
        matched +=1 
        if fout != None:
            fout.write(
                    ','.join( [ str(x) for x in
                        [l1, h1, bx1, chip1, strip1 ,bend1 ,z1,l2, h2, bx2, chip2, strip2 ,bend2 ,z2]
                        ]) + '\n'
                    )
    return matched


if __name__=="__main__":
    fin = open(args.file,"r")
    fout = open(args.out,"w")
    fout.write( ## write helper line
                ','.join([ 
                    "link1", "hyb1", "bx1", "chip1", "strip1" ,"bend1" ,"z1","link2", "hyb2", "bx2", "chip2", "strip2" ,"bend2" ,"z2"]) + '\n'
                )

    meta = {} ### metadata start storing metadata

    lastread = 0
    events = []

    offset_counts={ k:0 for k in range(-10,11)}

    for line in fin:
        if line.startswith('#'): 
            ## does the line contain a date?    
            try:
                meta['date'] = str( datetime.fromisoformat( re.sub('\n','',re.sub('^#*\ ','',line)) ) ) # str(datetime) is equivalent to toisoformat
                print("> the starting of datataking was", meta['date'] )
            except:
                pass

            continue
        iread = int(line.split()[0])
        link = int(line.split()[1])
        hyb = int(line.split()[2])
        # word = [3]
        nstub = int(line.split()[4])
        bx = int(line.split()[5])
        chip = int(line.split()[6])
        strip = int(line.split()[7])
        bend = int(line.split()[8])
        z = int(line.split()[9])
        
        ## do something
        if lastread != iread: 
            #print("Processing",lastread)
            if args.run_offset_scan:
                for k in offset_counts.keys():
                    offset_counts[k] += time_match(events,None,offset = k, window=0  )

            time_match(events,fout )
            events= []
            lastread=iread

        ## these events are not read correctly
        if nstub >1: continue 
        ## first event is not read correctly, if bram ar not reset
        if iread == 1 and args.ignore_first: continue 

        events.append( (link, hyb, bx, chip, strip ,bend ,z ))
    #flush
    #print("Processing",lastread)
    if args.run_offset_scan:
        print("Offset counts:")
        for k in offset_counts.keys():
            offset_counts[k] += time_match(events,None,offset = k, window=0  )
            print("* ",k, offset_counts[k])
        meta['offset'] = offset_counts[k]
        
    time_match(events,fout)
    events=[]
    fin.close()
    fout.close()
    
    meta['runtime'] = lastread ## time in minutes
    print(" Adding additional information to the run")

    ### second part after matching. Add information
    #### Add things -> TODO add to processing
    import pandas as pd 
    import math
    ## geometry
    from cosmics.geometry import *

    ## actual setup
    from cosmics.tower import tower
    m0 = tower.get('m0')
    m1 = tower.get('m1')

    meta['setup'] = tower.get_name()

    ## read the closed output file in pandas
    run = pd.read_csv(args.out)
    
    ## start adding information
    to_add = {"impact1-x":[],"impact1-y":[],"impact1-z":[],
              "impact2-x":[],"impact2-y":[],"impact2-z":[],
              "theta":[],
              "bend":[],
             }
    ## this is potentially slow. can we vectorize it
    for i in range(0, len(run)):
        s0 = m0.get(run.iloc[i]["hyb1"],run.iloc[i]["z1"], run.iloc[i]['chip1'],run.iloc[i]['strip1'])
        s1 = m1.get(run.iloc[i]["hyb2"],run.iloc[i]["z2"], run.iloc[i]['chip2'],run.iloc[i]['strip2'])

        p0 = (s0.start + s0.stop)/2.
        p1 = (s1.start + s1.stop)/2.

        to_add["impact1-x"].append(p0[0])
        to_add["impact1-y"].append(p0[1])
        to_add["impact1-z"].append(p0[2])

        to_add["impact2-x"].append(p1[0])
        to_add["impact2-y"].append(p1[1])
        to_add["impact2-z"].append(p1[2])

        to_add["theta"].append(   math.atan( math.sqrt(  (p0[1]-p1[1])**2 + (p0[2]-p1[2])**2) / abs(p0[0]-p1[0])  ) )
        to_add["bend"] .append(   math.atan(  (p0[1]-p1[1]) / abs(p0[0]-p1[0])  ))


    for col in to_add.keys():
        run[col] = np.array(to_add[col])
    
    meta['LUT-bend'] = 'fine-03'
    for i in range(1,3):
        run['bdec%d'%i] = run['bend%d'%i].map({
            0b000:0,
            0b001:1,
            0b010:2,
            0b011:3,
            0b101:-1,
            0b110:-2,
            0b100:-3,
            0b111:10,
            })
    
    print(" Writing updated csv file")
    run.to_csv(args.out)
    ## write metadata
    json_file_name = re.sub('csv','json',args.out)
    if json_file_name == args.out: json_file_name = args.out + '.json'
    with open(json_file_name,'w') as jout:
        json.dump( meta, jout)
    print ("-> Finished")
