from argparse import ArgumentParser
parser=ArgumentParser()
parser.add_argument("-f","--file",help="input file",default="cosmics1.txt")
parser.add_argument("-o","--out",help="output file",default="run1.csv")
parser.add_argument("--ignore_first",help="ignore first read (default)",default=True,action='store_true')
parser.add_argument("--do_first",help="do first read",dest='ignore_first',action='store_false')
args = parser.parse_args()
#args.ignore_first=True


def time_match(events, fout, verbose=False, window=1):
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
        if verbose: print("matching event",ie) 
        if closest[ie] <0 : continue ## no match
        if verbose: print(" > has a closest") 
        je = closest[ie]
        if closest[je] != ie: continue ## that guy has another better candidate
        if verbose: print(" > the other agrees") 
        l2, h2, bx2, chip2, strip2 ,bend2 ,z2 = events[je]
        if abs(bx1-bx2)> window : continue
        if verbose: print(" > bx is within window") 
        
        closest[je] = -1 ## avoid duplicate processing

        fout.write(
                ','.join( [ str(x) for x in
                    [l1, h1, bx1, chip1, strip1 ,bend1 ,z1,l2, h2, bx2, chip2, strip2 ,bend2 ,z2]
                    ]) + '\n'
                )
            


if __name__=="__main__":
    fin = open(args.file,"r")
    fout = open(args.out,"w")
    fout.write( ## write helper line
                ','.join([ 
                    "link1", "hyb1", "bx1", "chip1", "strip1" ,"bend1" ,"z1","link2", "hyb2", "bx2", "chip2", "strip2" ,"bend2" ,"z2"]) + '\n'
                )
    lastread = 0
    events = []

    for line in fin:
        if line.startswith('#'): continue
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
            print("Processing",lastread)
            time_match(events,fout, verbose = (lastread == 168) )
            events= []
            lastread=iread

        ## these events are not read correctly
        if nstub >1: continue 
        ## first event is not read correctly, if bram ar not reset
        if iread == 1 and args.ignore_first: continue 

        events.append( (link, hyb, bx, chip, strip ,bend ,z ))
    #flush
    print("Processing",lastread)
    time_match(events,fout)
    events=[]
    fin.close()
    fout.close()
