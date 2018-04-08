# The structure of the description of the analyzed waves in the program
class TWaveDescription(object):
    def __init__(self, name, numwave, subwaves):
        self.NameWave = name              # name of the wave
        self.NumWave = numwave            # number of sub-waves in a wave
        self.Subwaves = subwaves          # the names of the possible sub-waves in the wave


# A class for storing the parameters of a wave
class TWave(object):
    def __init__(self):
        self.Name = ''              # name of the wave
        self.Formula = ''           # the formula of the wave (1-2-3-4-5, <1-2-3 etc.)
        self.Level = 0              # the level of the wave
        self.ValueVertex = []       # the value of the top of the wave
        self.IndexVertex = []       # the indexes of the top of the waves

class TZigzag(object):
    def __init__(self):
        self.IndexVertex = []       # indexes of the vertexes of the zigzag
        self.ValueVertex = []       # value of the vertexes of the zigzags

# The structure for storing the points, found by the zigzag
class TPoints(object):
    def __init__(self):
        self.ValuePoints = []       # the values of the found points
        self.IndexPoints = []       # the indexes of the found points
        self.NumPoints = 0          # the number of found points


# +------------------------------------------------------------------+
# | The Zigzag function                                              |
# +------------------------------------------------------------------+
def ZigzagCreate(H, Start, Finish):
    IndexVertex = []
    ValueVertex = []
    Up=True
    dH=H #*Point()
    j=0
    TempMaxBar = Start
    TempMinBar = Start
    TempMax = rates[Start].high
    TempMin = rates[Start].low
    for i in range(Start+1, i<=Finish):
        # processing the case of a rising segment
        if Up:
             # check that the current maximum has not changed
            if(rates[i].high>TempMax):
                # if it has, correct the corresponding variables
                TempMax=rates[i].high
                TempMaxBar=i
            elif(rates[i].low<TempMax-dH):
                # otherwise, if the lagged level is broken, fixate the maximum
                ValueVertex.append(TempMax)
                IndexVertex.append(TempMaxBar)
                j+=1
                # correct the corresponding variables
                Up=False
                TempMin=rates[i].low
                TempMinBar=i
        else:
            # processing the case of the descending segment
            # check that the current minimum hasn't changed
            if(rates[i].low<TempMin):
               # if it has, correct the corresponding variables
               TempMin=rates[i].low
               TempMinBar=i
            elif(rates[i].high > TempMin+dH):
               # otherwise, if the lagged level is broken, fix the minimum
               ValueVertex.append(TempMin)
               IndexVertex.append(TempMinBar)
               j+=1
               # correct the corresponding variables
               Up=True
               TempMax=rates[i].high
               TempMaxBar=i

    # return the number of zigzag tops
    return j, IndexVertex, ValueVertex

def FindPoints(ZigzagArray, NumPoints, IndexStart, IndexFinish, ValueStart, ValueFinish, Points):
    n = 0
    # fill the array ZigzagArray
    for i in range(len(ZigzagArray)-1, 0, -1):
        Zigzag=ZigzagArray[i]             # the obtained i zigzag in the ZigzagArray
        IndexVertex=Zigzag.IndexVertex    # get the array of the indexes of the tops of the i zigzags
        ValueVertex=Zigzag.ValueVertex # get the array of values of the tops of the i zigzag
        Index1=-1,Index2=-1
        # search the index of the IndexVertex array, corresponding to the first point
        for j in range(0, len(IndexVertex)):
            if IndexVertex[j] >= IndexStart:
                Index1 = j
                break

            # search the index of the IndexVertex array, corresponding to the last point
            for j in range(len(IndexVertex)-1, 0, -1):
                if IndexVertex[j] <= IndexFinish:
                    Index2 = j
                    break

            # if the first and last points were found
            if (Index1 != -1) and (Index2 != -1):
                n=Index2-Index1+1 # find out how many points were found

            # if the required number of points was found (equal or greater)
            if n >= NumPoints:

                # check that the first and last tops correspond with the required top values
                if(((ValueStart!=0) and (ValueVertex.At(Index1)!=ValueStart)) or
                    ((ValueFinish!=0) and (ValueVertex.At(Index1+n-1)!=ValueFinish))): continue
                # fill the Points structure, passed as a parameter
                Points.NumPoints=n
                Points.ValuePoints = Points.ValuePoints[:n] #ArrayResize(Points.ValuePoints, n)
                Points.IndexPoints = Points.IndexPoints[:n]
                k=0
                # fill the ValuePoints and IndexPoints arrays of Points structure
                for j in range(Index1, Index1+n):
                    Points.ValuePoints[k]=ValueVertex[j]
                    Points.IndexPoints[k]=IndexVertex[j]
                    k += 1

                return True
    return False

#+-----------------------------------------------------------------------+
#| The function WaveAMoreWaveB checks whether or not the wave A is larger than the wave B, |
#| transferred as the parameters of the given function                     |
#| this check can be performed only if wave A - is complete,    |
#| and wave B - is incomplete or incomplete and unbegun               |
#+-----------------------------------------------------------------------+
def WaveAMoreWaveB(A, B, FixedVertex, ValueVertex, Trend):
    Result=0
    LengthWaveA=0
    LengthWaveB=0
    if FixedVertex[A]==1 and FixedVertex[A-1]==1 and (FixedVertex[B]==1 or FixedVertex[B-1]==1):
        LengthWaveA=abs(ValueVertex[A]-ValueVertex[A-1])
        if FixedVertex[B]==1 and FixedVertex[B-1]==1: LengthWaveB = abs(ValueVertex[B]-ValueVertex[B-1])
        elif FixedVertex[B]==1 and FixedVertex[B-1]==0:
            if Trend=="Up": LengthWaveB=abs(ValueVertex[B] - Minimum[B])
            else: LengthWaveB = abs(ValueVertex[B]-Maximum[B])
        elif FixedVertex[B]==0 and FixedVertex[B-1]==1:
            if Trend=="Up": LengthWaveB=abs(ValueVertex[B-1] - Minimum[B-1])
            else: LengthWaveB = abs(ValueVertex[B-1] - Maximum[B-1])
        if LengthWaveA > LengthWaveB: Result=1
        else: Result=-1
    return Result


class TNode(object):
    def __init__(self):
        self.Child = []    # the child of the given tree node
        self.Wave = TWave()      # the wave, stored in the given tree node
        self.Text = ''        # text of the tree node

    def Add(self, Text, Wave=None): # the function of adding the node to the tree
        Node = TNode()
        Node.Child=[]
        Node.Text=Text
        Node.Wave=Wave
        self.Child.append(Node)
        return Node


# A class for storing the parameters of the already analyzed section, corresponding to the wave tree node
class TNodeInfo(object):
    def __init__(self):
        self.IndexStart=0, self.IndexFinish=0   # the range of the already analyzed section
        self.ValueStart=0, self.ValueFinish=0   # the edge value of the already analyzed section
        self.Subwaves=''                        # the name of the wave and the group of the waves
        self.Node = TNode()                     # the node, pointing to the already analyzed range of the chart


class ElliotWave(object):
    def __init__(self):
        waveDescriotion = []

        waveDescriotion.append(TWaveDescription("Impulse", 5,
                    ["", "Impulse,Leading Diagonal,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Impulse,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Impulse,Diagonal,"]))

        waveDescriotion.append(TWaveDescription("Leading Diagonal", 5,
                    ["",
                    "Impulse,Leading Diagonal,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Impulse,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Impulse,Diagonal,"]))

        waveDescriotion.append(TWaveDescription("Diagonal", 5,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,"]))

        waveDescriotion.append(TWaveDescription("Zigzag", 3,
                    ["",
                    "Impulse,Leading Diagonal,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Impulse,Diagonal,",
                    "",
                    ""]))

        waveDescriotion.append(TWaveDescription("Flat", 3,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Impulse,Diagonal,",
                    "",
                    ""]))

        waveDescriotion.append(TWaveDescription("Double Zigzag", 3,
                    ["",
                    "Zigzag,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,",
                    "",
                    ""]))

        waveDescriotion.append(TWaveDescription("Triple Zigzag", 5,
                    ["",
                    "Zigzag,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,"]))

        waveDescriotion.append(TWaveDescription("Double Three", 3,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "",
                    ""]))

        waveDescriotion.append(TWaveDescription("Triple Three", 5,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,"]))

        waveDescriotion.append(TWaveDescription("Contracting Triangle", 5,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,"]))

        waveDescriotion.append(TWaveDescription("Expanding Triangle", 5,
                    ["",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
                    "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,"
                    ]))


def FillZigzagArray(Start,Finish):
    ZigzagArray=[]          # create the dynamic array of zigzags
    #IndexVertex=[]          # create the dynamic array of indexes of zigzag tops
    #ValueVertex=[]          # create the dynamic array of values of the zigzag tops
    H=1
    j=0
    n, IndexVertex, ValueVertex = ZigzagCreate(H,Start,Finish)#find the tops of the zigzag with the parameter H=1
    if n>0:
        # store the tops of the zigzag in the array ZigzagArray
        Zigzag=TZigzag() # create the object for storing the found indexes and the zigzag tops,
                             # fill it and store in the array ZigzagArray
        Zigzag.IndexVertex=IndexVertex
        Zigzag.ValueVertex=ValueVertex
        ZigzagArray.append(Zigzag)
        j+=1

    H+=1
    # loop of the H of the zigzag
    while True:
        n, IndexVertex, ValueVertex = ZigzagCreate(H,Start,Finish) # find the tops of the zigzag
        if n > 0:
            Zigzag=ZigzagArray[j-1]
            PrevIndexVertex=Zigzag.IndexVertex # get the array of indexes of the previous zigzag
            b = False
            # check if there is a difference between the current zigzag and the previous zigzag
            for i in range(0, n-1):
                if PrevIndexVertex[i]!=IndexVertex[i]:
                    #
                    # if there is a difference, store the tops of a zigzag in the array ZigzagArray
                   Zigzag = TZigzag()
                   Zigzag.IndexVertex=IndexVertex
                   Zigzag.ValueVertex=ValueVertex
                   ZigzagArray.append(Zigzag)
                   j+=
                   b=True
                   break

            #if b == False:
            #    # otherwise, if there is no difference, release the memory
            #    IndexVertex = []
            #    ValueVertex = []
        # search for the tops of the zigzag until there is two or less of them
        if n<=2: break
        H+=1
