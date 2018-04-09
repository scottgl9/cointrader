# The structure of the description of the analyzed waves in the program
class TWaveDescription(object):
    def __init__(self, name='', numwave=0, subwaves=[]):
        self.NameWave = name  # name of the wave
        self.NumWave = numwave  # number of sub-waves in a wave
        self.Subwaves = subwaves  # the names of the possible sub-waves in the wave

# A class for storing the parameters of a wave
class TWave(object):
    def __init__(self):
        self.Name = ''  # name of the wave
        self.Formula = ''  # the formula of the wave (1-2-3-4-5, <1-2-3 etc.)
        self.Level = 0  # the level of the wave
        self.ValueVertex = [0.0] * 6  # the value of the top of the wave
        self.IndexVertex = [-1] * 6  # the indexes of the top of the waves

class TZigzag(object):
    def __init__(self):
        self.IndexVertex = []  # indexes of the vertexes of the zigzag
        self.ValueVertex = []  # value of the vertexes of the zigzags

# The structure for storing the points, found by the zigzag
class TPoints(object):
    def __init__(self):
        self.ValuePoints = []  # the values of the found points
        self.IndexPoints = []  # the indexes of the found points
        self.NumPoints = 0  # the number of found points


class TNode(object):
    def __init__(self):
        self.Child = []  # the child of the given tree node
        self.Wave = TWave()  # the wave, stored in the given tree node
        self.Text = ''  # text of the tree node

    def Add(self, Text='', Wave=None):  # the function of adding the node to the tree
        Node = TNode()
        Node.Child = []
        Node.Text = Text
        Node.Wave = Wave
        self.Child.append(Node)
        return Node

Maximum = [None] * 6
Minimum = [None] * 6
Trend = 'Up'

# +-------------------------------------------------------------------------------------+
# | The function VertexAAboveVertexB checks whether or not the top A is higher than top B,        |
# | transferred as the parameters of the given function                                   |
# | this check can be performed only if the tops A and B - are fixed,          |
# | or the top A - is not fixed and prime, while the top B - is fixed,             |
# | or the top A - is fixed, while the top B - is not fixed and odd,           |
# | or the top A - is not fixed and prime, and the top B - is not fixed and odd |
# +-------------------------------------------------------------------------------------+
def VertexAAboveVertexB(A, B, InternalPoints, FixedVertex=None, ValueVertex=None):
    VA = 0
    VB = 0
    VC = 0
    IA = 0
    IB = 0
    Result = 0
    if A >= B:
        IA = A
        IB = B
    elif A < B:
        IA = B
        IB = A
    # if the internal points of the wave must be taken into consideration
    if InternalPoints:
        if Trend == "Up" and ((IA % 2 == 0) or ((IA - IB == 1) and (IB % 2 == 0))):
            VA = Minimum[IA]
            IA = IA - IA % 2
        elif Trend == "Down" and ((IA % 2 == 0) or ((IA - IB == 1) and (IB % 2 == 0))):
            VA = Maximum[IA]
            IA = IA - IA % 2
        elif (Trend == "Up") and ((IA % 2 == 1) or ((IA - IB == 1) and (IB % 2 == 1))):
            VA = Maximum[IA]
            IA = IA - (1 - IA % 2)
        elif (Trend == "Down") and (IA % 2 == 1) or ((IA - IB == 1) and (IB % 2 == 1)):
            VA = Minimum[IA]
            IA = IA - (1 - IA % 2)
        VB = ValueVertex[IB]
    else:
        VA = ValueVertex[IA]
        VB = ValueVertex[IB]
    if A > B:
        A = IA
        B = IB
    elif A < B:
        A = IB
        B = IA
        VC = VA
        VA = VB
        VB = VC
    if (((FixedVertex[A] == 1) and (FixedVertex[B] == 1)) or
            ((FixedVertex[A] == 0) and (A % 2 == 0) and (FixedVertex[B] == 1)) or
            ((FixedVertex[A] == 1) and (FixedVertex[B] == 0) and (B % 2 == 1)) or
            ((FixedVertex[A] == 0) & (A % 2 == 0) and (FixedVertex[B] == 0) and (B % 2 == 1))):
        if ((Trend == "Up") and (VA >= VB)) or ((Trend == "Down") and (VA <= VB)):
            Result = 1
        else:
            Result = -1
    return Result


# A class for storing the parameters of the already analyzed section, corresponding to the wave tree node
class TNodeInfo(object):
    def __init__(self):
        self.IndexStart = 0
        self.IndexFinish = 0  # the range of the already analyzed section
        self.ValueStart = 0
        self.ValueFinish = 0  # the edge value of the already analyzed section
        self.Subwaves = ''  # the name of the wave and the group of the waves
        self.Node = TNode()  # the node, pointing to the already analyzed range of the chart


class ElliotWave(object):
    def __init__(self):
        waveDescriotion = BuildWaveDescription()


def BuildWaveDescription():
    waveDescriotion = []

    waveDescriotion.append(TWaveDescription("Impulse", 5,
        ["", "Impulse,Leading Diagonal,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
         "Impulse,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
         "Impulse,Diagonal,"]))

    waveDescriotion.append(TWaveDescription("Leading Diagonal", 5,
        ["", "Impulse,Leading Diagonal,",
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
         "", ""]))

    waveDescriotion.append(TWaveDescription("Triple Zigzag", 5,
        ["",
         "Zigzag,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
         "Zigzag,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Triple Three,Contracting Triangle,Expanding Triangle,", "Zigzag,"]))

    waveDescriotion.append(TWaveDescription("Double Three", 3,
        ["",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,",
         "", ""]))

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
         "Zigzag,Flat,Double Zigzag,Triple Zigzag,Double Three,Triple Three,Contracting Triangle,Expanding Triangle,"]))

    return waveDescriotion


WaveDescription = BuildWaveDescription()


# +------------------------------------------------------------------+
# | The Zigzag function                                              |
# +------------------------------------------------------------------+
def ZigzagCreate(rates, H, Start, Finish):
    IndexVertex = []
    ValueVertex = []
    Up = True
    dH = H  # *Point()
    j = 0
    TempMaxBar = Start
    TempMinBar = Start
    TempMax = rates[Start].high
    TempMin = rates[Start].low

    for i in range(Start + 1, Finish):
        # processing the case of a rising segment
        if Up:
            # check that the current maximum has not changed
            if (rates[i].high > TempMax):
                # if it has, correct the corresponding variables
                TempMax = rates[i].high
                TempMaxBar = i
            elif rates[i].low < TempMax - dH:
                # otherwise, if the lagged level is broken, fixate the maximum
                ValueVertex.append(TempMax)
                IndexVertex.append(TempMaxBar)
                j += 1
                # correct the corresponding variables
                Up = False
                TempMin = rates[i].low
                TempMinBar = i
        else:
            # processing the case of the descending segment
            # check that the current minimum hasn't changed
            if rates[i].low < TempMin:
                # if it has, correct the corresponding variables
                TempMin = rates[i].low
                TempMinBar = i
            elif rates[i].high > TempMin + dH:
                # otherwise, if the lagged level is broken, fix the minimum
                ValueVertex.append(TempMin)
                IndexVertex.append(TempMinBar)
                j += 1
                # correct the corresponding variables
                Up = True
                TempMax = rates[i].high
                TempMaxBar = i

    # return the number of zigzag tops
    return j, IndexVertex, ValueVertex


def FillZigzagArray(Start, Finish):
    ZigzagArray = []  # create the dynamic array of zigzags
    # IndexVertex=[]         # create the dynamic array of indexes of zigzag tops
    # ValueVertex=[]         # create the dynamic array of values of the zigzag tops
    H = 1
    j = 0
    n, IndexVertex, ValueVertex = ZigzagCreate(H, Start, Finish)  # find the tops of the zigzag with the parameter H=1
    if n > 0:
        # store the tops of the zigzag in the array ZigzagArray
        Zigzag = TZigzag()  # create the object for storing the found indexes and the zigzag tops,
        # fill it and store in the array ZigzagArray
        Zigzag.IndexVertex = IndexVertex
        Zigzag.ValueVertex = ValueVertex
        ZigzagArray.append(Zigzag)
        j += 1

    H += 1
    # loop of the H of the zigzag
    while True:
        n, IndexVertex, ValueVertex = ZigzagCreate(H, Start, Finish)  # find the tops of the zigzag
        if n > 0:
            Zigzag = ZigzagArray[j - 1]
            PrevIndexVertex = Zigzag.IndexVertex  # get the array of indexes of the previous zigzag
            b = False
            # check if there is a difference between the current zigzag and the previous zigzag
            for i in range(0, n - 1):
                if PrevIndexVertex[i] != IndexVertex[i]:
                    #
                    # if there is a difference, store the tops of a zigzag in the array ZigzagArray
                    Zigzag = TZigzag()
                    Zigzag.IndexVertex = IndexVertex
                    Zigzag.ValueVertex = ValueVertex
                    ZigzagArray.append(Zigzag)
                    j += 1
                    b = True
                    break

            # if b == False:
            #    # otherwise, if there is no difference, release the memory
            #    IndexVertex = []
            #    ValueVertex = []
        # search for the tops of the zigzag until there is two or less of them
        if n <= 2: break
        H += 1


def FindPoints(ZigzagArray, NumPoints, IndexStart, IndexFinish, ValueStart, ValueFinish, Points):
    n = 0
    # fill the array ZigzagArray
    for i in range(len(ZigzagArray) - 1, 0, -1):
        Zigzag = ZigzagArray[i]  # the obtained i zigzag in the ZigzagArray
        IndexVertex = Zigzag.IndexVertex  # get the array of the indexes of the tops of the i zigzags
        ValueVertex = Zigzag.ValueVertex  # get the array of values of the tops of the i zigzag
        Index1 = -1, Index2 = -1
        # search the index of the IndexVertex array, corresponding to the first point
        for j in range(0, len(IndexVertex)):
            if IndexVertex[j] >= IndexStart:
                Index1 = j
                break

        # search the index of the IndexVertex array, corresponding to the last point
        for j in range(len(IndexVertex) - 1, 0, -1):
            if IndexVertex[j] <= IndexFinish:
                Index2 = j
                break

        # if the first and last points were found
        if (Index1 != -1) and (Index2 != -1):
            n = Index2 - Index1 + 1  # find out how many points were found

        # if the required number of points was found (equal or greater)
        if n >= NumPoints:

            # check that the first and last tops correspond with the required top values
            if (((ValueStart != 0) and (ValueVertex.At(Index1) != ValueStart)) or
                    ((ValueFinish != 0) and (ValueVertex.At(Index1 + n - 1) != ValueFinish))): continue
            # fill the Points structure, passed as a parameter
            Points.NumPoints = n
            Points.ValuePoints = Points.ValuePoints[:n]  # ArrayResize(Points.ValuePoints, n)
            Points.IndexPoints = Points.IndexPoints[:n]
            k = 0
            # fill the ValuePoints and IndexPoints arrays of Points structure
            for j in range(Index1, Index1 + n):
                Points.ValuePoints[k] = ValueVertex[j]
                Points.IndexPoints[k] = IndexVertex[j]
                k += 1
            return True
    return False


# +-----------------------------------------------------------------------+
# | The function WaveAMoreWaveB checks whether or not the wave A is larger than the wave B, |
# | transferred as the parameters of the given function                     |
# | this check can be performed only if wave A - is complete,    |
# | and wave B - is incomplete or incomplete and unbegun               |
# +-----------------------------------------------------------------------+
def WaveAMoreWaveB(A, B, FixedVertex=None, ValueVertex=None):
    Result = 0
    LengthWaveA = 0
    LengthWaveB = 0
    if FixedVertex[A] == 1 and FixedVertex[A - 1] == 1 and (FixedVertex[B] == 1 or FixedVertex[B - 1] == 1):
        LengthWaveA = abs(ValueVertex[A] - ValueVertex[A - 1])
        if FixedVertex[B] == 1 and FixedVertex[B - 1] == 1:
            LengthWaveB = abs(ValueVertex[B] - ValueVertex[B - 1])
        elif FixedVertex[B] == 1 and FixedVertex[B - 1] == 0:
            if Trend == "Up":
                LengthWaveB = abs(ValueVertex[B] - Minimum[B])
            else:
                LengthWaveB = abs(ValueVertex[B] - Maximum[B])
        elif FixedVertex[B] == 0 and FixedVertex[B - 1] == 1:
            if Trend == "Up":
                LengthWaveB = abs(ValueVertex[B - 1] - Minimum[B - 1])
            else:
                LengthWaveB = abs(ValueVertex[B - 1] - Maximum[B - 1])
        if LengthWaveA > LengthWaveB:
            Result = 1
        else:
            Result = -1
    return Result


def FindWaveInWaveDescription(NameWave):
    for i in range(0, len(WaveDescription)):
        if WaveDescription[i].NameWave == NameWave: return i
    return -1


def WaveRules(Wave, IndexVertex=None, ValueVertex=None, FixedVertex=None,rates=None):
    Formula = Wave.Formula
    Result = False

    for i in range(0, 5):
        IndexVertex[i] = Wave.IndexVertex[i]
        ValueVertex[i] = Wave.ValueVertex[i]
        FixedVertex[i] = -1

    Pos1 = Formula.find('<') #StringFind(Formula, "<")
    if Pos1 > 0:
        Str = Formula[Pos1 - 1] #ShortToString(StringGetCharacter(Formula, Pos1 - 1))
        FixedVertex[int(Str)] = 1
        FixedVertex[int(Str) - 1] = 0
        Pos1 = int(Str) + 1

    else:
        Pos1 = 0
    Pos2 = Formula.find('<') #StringFind(Formula, ">")
    if Pos2 > 0:
        Str = Formula[Pos2 - 1] #ShortToString(StringGetCharacter(Formula, Pos2 - 1))
        FixedVertex[int(Str)] = 0
        Pos2 = int(Str) - 1

    else:
        Pos2 = len(Formula)
        Str = Formula[Pos2 - 1] #ShortToString(StringGetCharacter(Formula, Pos2 - 1))
        Pos2 = int(Str)

    for i in range(Pos1, Pos2):
        FixedVertex[i] = 1

    #ArrayResize(High, ArrayRange(rates, 0))
    #ArrayResize(Low, ArrayRange(rates, 0))
    # find the maximums and minimums of the waves
    for i in range(1, 5):
        Maximum[i] = rates[IndexVertex[i]].high
        Minimum[i] = rates[IndexVertex[i - 1]].low
        for j in range(IndexVertex[i - 1], IndexVertex[i]):
            if rates[j].high > Maximum[i]: Maximum[i] = rates[j].high
            if rates[j].low < Minimum[i]: Minimum[i] = rates[j].low

    # find out the trend
    if ((FixedVertex[0] == 1 and ValueVertex[0] == rates[IndexVertex[0]].low) or
            (FixedVertex[1] == 1 and ValueVertex[1] == rates[IndexVertex[1]].high) or
            (FixedVertex[2] == 1 and ValueVertex[2] == rates[IndexVertex[2]].low) or
            (FixedVertex[3] == 1 and ValueVertex[3] == rates[IndexVertex[3]].high) or
            (FixedVertex[4] == 1 and ValueVertex[4] == rates[IndexVertex[4]].low) or
            (FixedVertex[5] == 1 and ValueVertex[5] == rates[IndexVertex[5]].high)):
        Trend = "Up"
    else:
        Trend = "Down"
    # check the required wave by the rules
    if Wave.Name == "Impulse" and VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and \
            VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and \
            VertexAAboveVertexB(3, 1, False) >= 0 and VertexAAboveVertexB(4, 1, True) >= 0 and \
            VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, True) >= 0 and (
            WaveAMoreWaveB(3, 1) >= 0 or WaveAMoreWaveB(3, 5) >= 0):
        Result = True
    elif Wave.Name == "Leading Diagonal" and VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and \
            VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and \
            VertexAAboveVertexB(3, 1, False) >= 0 and VertexAAboveVertexB(4, 2, True) >= 0 and \
            VertexAAboveVertexB(1, 4, False) >= 0 and \
            VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, True) >= 0 and \
            (WaveAMoreWaveB(3, 1) >= 0 or WaveAMoreWaveB(3, 5) >= 0):
        Result = True
    elif Wave.Name == "Diagonal" and (VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and
                                      VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and
                                      VertexAAboveVertexB(3, 1, False) >= 0 and VertexAAboveVertexB(4, 2, True) >= 0 and
                                      VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, True) >= 0 and
                                      (WaveAMoreWaveB(3, 1) >= 0 or WaveAMoreWaveB(3, 5) >= 0)):
        Result = True
    elif Wave.Name == "Zigzag" and (VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and
                                    VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and
                                    VertexAAboveVertexB(3, 1, False) >= 0):
        Result = True

    elif Wave.Name == "Flat" and (VertexAAboveVertexB(1, 0, False) >= 0 and
                                  VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0):
        Result = True

    elif Wave.Name == "Double Zigzag" and (
            VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and
            VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and
            VertexAAboveVertexB(3, 1, False) >= 0):
        Result = True

    elif Wave.Name == "Double Three" and (VertexAAboveVertexB(1, 0, True) >= 0 and
                                          VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, False) >= 0):
        Result = True

    elif Wave.Name == "Triple Zigzag" and (
            VertexAAboveVertexB(1, 0, True) >= 0 and VertexAAboveVertexB(2, 0, True) >= 0 and
            VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, True) >= 0 and
            VertexAAboveVertexB(3, 1, False) >= 0 and VertexAAboveVertexB(5, 3, False) and
            VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, True) >= 0):
        Result = True

    elif Wave.Name == "Triple Three" and (VertexAAboveVertexB(1, 0, True) >= 0 and
                                          VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2,
                                                                                                        False) >= 0 and
                                          VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4,
                                                                                                        False) >= 0):
        Result = True

    elif Wave.Name == "Contracting Triangle" and (
            VertexAAboveVertexB(1, 0, False) >= 0 and VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, False) >= 0 and
            VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, False) >= 0 and
            WaveAMoreWaveB(2, 3) >= 0 and WaveAMoreWaveB(3, 4) >= 0 and WaveAMoreWaveB(4, 5) >= 0):
        Result = True

    elif Wave.Name == "Expanding Triangle" and (
            VertexAAboveVertexB(1, 0, False) >= 0 and VertexAAboveVertexB(1, 2, False) >= 0 and VertexAAboveVertexB(3, 2, False) >= 0 and
            VertexAAboveVertexB(3, 4, False) >= 0 and VertexAAboveVertexB(5, 4, False) >= 0 and
            WaveAMoreWaveB(3, 2) >= 0 and WaveAMoreWaveB(3, 2) >= 0):
        Result = True

    return Result


# +------------------------------------------------------------------+
# | The NotStartedAndNotFinishedWaves function                       |
# +------------------------------------------------------------------+
def NotStartedAndNotFinishedWaves(ParentWave, NumWave, Node, Subwaves, Level):
    Points = TPoints()
    ParentNode = None
    ChildNode = None
    IndexWave = 0
    NameWave = []
    Wave = TWave()
    i = 0
    pos = 0
    start = 0

    #ArrayResize(ListNameWave, ArrayRange(WaveDescription, 0))
    #while pos != len(Subwaves) - 1:
    #    pos = StringFind(Subwaves, ",", start)
    #    NameWave = StringSubstr(Subwaves, start, pos - start)
    #    ListNameWave[i] = NameWave
    #    i += 1
    #    start = pos + 1

    # Put the waves, which we will be analyzing to the ListNameWave array
    ListNameWave = [None] * len(WaveDescriotion)
    for part in Subwaves.split(','):
        ListNameWave[i] = part
        i += 1

    IndexStart = ParentWave.IndexVertex[NumWave - 1]
    IndexFinish = ParentWave.IndexVertex[NumWave]
    ValueStart = ParentWave.ValueVertex[NumWave - 1]
    ValueFinish = ParentWave.ValueVertex[NumWave]

    # find no less than two points on the price chart and put them into the structure Points
    # if they are not found, then exit the function
    if FindPoints(2, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of unbegun and incomplete waves with the formula "1<-2-3>"
    v1 = 0
    while v1 <= Points.NumPoints - 2:
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 1):
            j = 0
            while j <= i - 1:
                # get the name of the wave for analysis from the ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the structure WaveDescription in order to
                # find out the number of its sub-waves and their names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if (WaveDescription[IndexWave].NumWave == 5) or (WaveDescription[IndexWave].NumWave == 3):
                    # create the object of TWave class and fill its fields - parameters of the analyzed waves
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "1<-2-3>"
                    Wave.ValueVertex[0] = 0
                    Wave.ValueVertex[1] = Points.ValuePoints[v1]
                    Wave.ValueVertex[2] = Points.ValuePoints[v2]
                    Wave.ValueVertex[3] = 0
                    Wave.ValueVertex[4] = 0
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = IndexStart
                    Wave.IndexVertex[1] = Points.IndexPoints[v1]
                    Wave.IndexVertex[2] = Points.IndexPoints[v2]
                    Wave.IndexVertex[3] = IndexFinish
                    Wave.IndexVertex[4] = 0
                    Wave.IndexVertex[5] = 0
                    # check the wave by the rules
                    if WaveRules(Wave) == True:
                        # if a wave passed the check by rules, add it into the wave tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 1
                        # create the first sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the second sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create a third sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

            v2 = v2 + 2
        v1 = v1 + 2

    # the loop of unbegun and unfinished waves with the formula "2<-3-4>"
    v2 = 0
    while (v2 <= Points.NumPoints - 2):
        v3 = v2 + 1
        while (v3 <= Points.NumPoints - 1):
            j = 0
            while (j <= i - 1):
                # get the name of the wave for analysis from the ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the WaveDescription structure in order to know the number of its symbols and its names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if (WaveDescription[IndexWave].NumWave == 5):
                    # create the object of TWave class and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "2<-3-4>"
                    Wave.ValueVertex[0] = 0
                    Wave.ValueVertex[1] = 0
                    Wave.ValueVertex[2] = Points.ValuePoints[v2]
                    Wave.ValueVertex[3] = Points.ValuePoints[v3]
                    Wave.ValueVertex[4] = 0
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = 0
                    Wave.IndexVertex[1] = IndexStart
                    Wave.IndexVertex[2] = Points.IndexPoints[v2]
                    Wave.IndexVertex[3] = Points.IndexPoints[v3]
                    Wave.IndexVertex[4] = IndexFinish
                    Wave.IndexVertex[5] = 0
                    # check the wave by the rules
                    if WaveRules(Wave):
                        # if the wave passed the check for rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 2
                        # create the second sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the third sub-wave in th waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the fourth sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

            v3 = v3 + 2
        v2 = v2 + 2

    # the loop of the unbegun and the incomplete waves with the formula "3<-4-5>"
    v3 = 0
    while (v3 <= Points.NumPoints - 2):
        v4 = v3 + 1
        while (v4 <= Points.NumPoints - 1):
            j = 0
            while (j <= i - 1):
                # get the name of the wave for analysis from the ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the WaveDescription structure in order to
                # find out the number of its symbols and their names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if (WaveDescription[IndexWave].NumWave == 5):
                    # create the object of TWave class and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "3<-4-5>"
                    Wave.ValueVertex[0] = 0
                    Wave.ValueVertex[1] = 0
                    Wave.ValueVertex[2] = 0
                    Wave.ValueVertex[3] = Points.ValuePoints[v3]
                    Wave.ValueVertex[4] = Points.ValuePoints[v4]
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = 0
                    Wave.IndexVertex[1] = 0
                    Wave.IndexVertex[2] = IndexStart
                    Wave.IndexVertex[3] = Points.IndexPoints[v3]
                    Wave.IndexVertex[4] = Points.IndexPoints[v4]
                    Wave.IndexVertex[5] = IndexFinish
                    # check the wave for the rules
                    if (WaveRules(Wave) == True):
                        # if the wave passed the check by the rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 3
                        # create the third sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the fourth sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the fifth sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the fifth wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                v4 = v4 + 2
            v3 = v3 + 2
    # find no less than three points on the price chart and put them in the Points structure
    # if they were not found, then exit the function
    if FindPoints(3, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False:
        return
    # the loop of unbegun and unfinished waved with the formula "1<-2-3-4>"
    v1 = 0
    while (v1 <= Points.NumPoints - 3):
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 2):
            v3 = v2 + 1
            while (v3 <= Points.NumPoints - 1):
                j = 0
                while (j <= i - 1):
                    # get the name of the wave for analysis from the ListNameWave
                    NameWave = ListNameWave[j]
                    j += 1
                    # find the index of the wave in the WaveDescription structure in order to know the number of its sub-waves and their names
                    IndexWave = FindWaveInWaveDescription(NameWave)
                    if WaveDescription[IndexWave].NumWave == 5:
                        # create an object of TWave class and fill its fields - parameters of the analyzed wave
                        Wave = TWave()
                        Wave.Name = NameWave
                        Wave.Level = Level
                        Wave.Formula = "1<-2-3-4>"
                        Wave.ValueVertex[0] = 0
                        Wave.ValueVertex[1] = Points.ValuePoints[v1]
                        Wave.ValueVertex[2] = Points.ValuePoints[v2]
                        Wave.ValueVertex[3] = Points.ValuePoints[v3]
                        Wave.ValueVertex[4] = 0
                        Wave.ValueVertex[5] = 0
                        Wave.IndexVertex[0] = IndexStart
                        Wave.IndexVertex[1] = Points.IndexPoints[v1]
                        Wave.IndexVertex[2] = Points.IndexPoints[v2]
                        Wave.IndexVertex[3] = Points.IndexPoints[v3]
                        Wave.IndexVertex[4] = IndexFinish
                        Wave.IndexVertex[5] = 0
                        # check the wave by the rules
                        if (WaveRules(Wave) == True):
                            # if the wave passed the check by the rules, add it to the waves tree
                            ParentNode = Node.Add(NameWave, Wave)
                            I = 1
                            # create the first sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the second sub-wave in the waved tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the third sub-wave in the waves
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the fourth sub-wave of the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                v3 = v3 + 2
            v2 = v2 + 2
        v1 = v1 + 2

    # the loop of unbegun and unfinished waves with the formula "2<-3-4-5>"
    v2 = 0
    while (v2 <= Points.NumPoints - 3):
        v3 = v2 + 1
        while (v3 <= Points.NumPoints - 2):
            v4 = v3 + 1
            while (v4 <= Points.NumPoints - 1):
                j = 0
                while j <= i - 1:
                    # get the name of the wave for analysis from the ListNameWave
                    NameWave = ListNameWave[j]
                    j += 1
                    # find the index of the wave in the WaveDescription structure in order to know the number of the symbols and their names
                    IndexWave = FindWaveInWaveDescription(NameWave)
                    if (WaveDescription[IndexWave].NumWave == 5):
                        # create the object of TWave class and fill its fields - parameters of the analyzed wave
                        Wave = TWave()
                        Wave.Name = NameWave
                        Wave.Level = Level
                        Wave.Formula = "2<-3-4-5>"
                        Wave.ValueVertex[0] = 0
                        Wave.ValueVertex[1] = 0
                        Wave.ValueVertex[2] = Points.ValuePoints[v2]
                        Wave.ValueVertex[3] = Points.ValuePoints[v3]
                        Wave.ValueVertex[4] = Points.ValuePoints[v4]
                        Wave.ValueVertex[5] = 0
                        Wave.IndexVertex[0] = 0
                        Wave.IndexVertex[1] = IndexStart
                        Wave.IndexVertex[2] = Points.IndexPoints[v2]
                        Wave.IndexVertex[3] = Points.IndexPoints[v3]
                        Wave.IndexVertex[4] = Points.IndexPoints[v4]
                        Wave.IndexVertex[5] = IndexFinish
                        # check the wave by the rules
                        if WaveRules(Wave):
                            # if the wave passed the check by the rules, add it to the waves tree
                            ParentNode = Node.Add(NameWave, Wave)
                            I = 2
                            # create the second sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the third sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the fourth sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the fifth sub-wave in the waved tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                v4 = v4 + 2
            v3 = v3 + 2
        v2 = v2 + 2
    # find no less than four point on the price chart and put them into the structure Points
    # if we didn't find any, then exit the function
    if (FindPoints(4, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False): return
    # the loop of unbegun and unfinished waves with the formula "1<-2-3-4-5>"
    v1 = 0
    while (v1 <= Points.NumPoints - 4):
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 3):
            v3 = v2 + 1
            while (v3 <= Points.NumPoints - 2):
                v4 = v3 + 1
                while (v4 <= Points.NumPoints - 1):
                    j = 0
                    while (j <= i - 1):
                        # get the name of the wave for analysis from the ListNameWave
                        NameWave = ListNameWave[j]
                        j += 1
                        # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
                        IndexWave = FindWaveInWaveDescription(NameWave)
                        if (WaveDescription[IndexWave].NumWave == 5):
                            # create the object TWave class and fill its fields - parameters of the analyzed wave
                            Wave = TWave()
                            Wave.Name = NameWave
                            Wave.Level = Level
                            Wave.Formula = "1<-2-3-4-5>"
                            Wave.ValueVertex[0] = 0
                            Wave.ValueVertex[1] = Points.ValuePoints[v1]
                            Wave.ValueVertex[2] = Points.ValuePoints[v2]
                            Wave.ValueVertex[3] = Points.ValuePoints[v3]
                            Wave.ValueVertex[4] = Points.ValuePoints[v4]
                            Wave.ValueVertex[5] = 0
                            Wave.IndexVertex[0] = IndexStart
                            Wave.IndexVertex[1] = Points.IndexPoints[v1]
                            Wave.IndexVertex[2] = Points.IndexPoints[v2]
                            Wave.IndexVertex[3] = Points.IndexPoints[v3]
                            Wave.IndexVertex[4] = Points.IndexPoints[v4]
                            Wave.IndexVertex[5] = IndexFinish
                            # check the wave by the rules
                            if (WaveRules(Wave) == True):
                                # if the wave passed the check by the rules, add it to the waves tree
                                ParentNode = Node.Add(NameWave, Wave)
                                I = 1
                                # create the first sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the first sub-wave has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the second sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the third sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the fourth sub-wave in the waved tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the 5th sub-wave in the wave tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        # otherwise, if the wave did not pass the check by the rules, release the memory
                        # else delete Wave
                    v4 = v4 + 2
                v3 = v3 + 2
            v2 = v2 + 2
        v1 = v1 + 2
    # find no less than one point on the price chart and record it into the structure Points
    # if we didn't find any, then exit the function
    if FindPoints(1, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of unbegun and unfinished waves with the formula "1<-2>"
    v1 = 0
    while (v1 <= Points.NumPoints - 1):
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if (WaveDescription[IndexWave].NumWave == 5 or WaveDescription[IndexWave].NumWave == 3):
                # create the object of TWave class and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "1<-2>"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = Points.ValuePoints[v1]
                Wave.ValueVertex[2] = 0
                Wave.ValueVertex[3] = 0
                Wave.ValueVertex[4] = 0
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = IndexStart
                Wave.IndexVertex[1] = Points.IndexPoints[v1]
                Wave.IndexVertex[2] = IndexFinish
                Wave.IndexVertex[3] = 0
                Wave.IndexVertex[4] = 0
                Wave.IndexVertex[5] = 0
                # check the wave by the rules
                if WaveRules(Wave) == True:
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 1
                    # create the first sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                    if (Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False):
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the second sub-wave in the waved tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                    if (Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False):
                        NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
        v1 = v1 + 1
    # loop the unbegun and unfinished waves with the formula "2<-3>"
    v2 = 0
    while (v2 <= Points.NumPoints - 1):
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the structure WaveDescription, in order to know the number of its sub-waves and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if (WaveDescription[IndexWave].NumWave == 5 or WaveDescription[IndexWave].NumWave == 3):
                # create the object of TWave class and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "2<-3>"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = 0
                Wave.ValueVertex[2] = Points.ValuePoints[v2]
                Wave.ValueVertex[3] = 0
                Wave.ValueVertex[4] = 0
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = 0
                Wave.IndexVertex[1] = IndexStart
                Wave.IndexVertex[2] = Points.IndexPoints[v2]
                Wave.IndexVertex[3] = IndexFinish
                Wave.IndexVertex[4] = 0
                Wave.IndexVertex[5] = 0
                # check the wave by the rules
                if WaveRules(Wave):
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 2
                    # create the second sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the third sub-wave in the waved tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                # otherwise, if the wave did not pass by the rules, release the memory
                # else delete Wave
        v2 = v2 + 1
        # the loop of unbegun and unfinished waves with the formula "3<-4>"
    v3 = 0
    while (v3 <= Points.NumPoints - 1):
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure on order to know the number of sub-waved and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if WaveDescription[IndexWave].NumWave == 5:
                # create the object of TWave class and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "3<-4>"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = 0
                Wave.ValueVertex[2] = 0
                Wave.ValueVertex[3] = Points.ValuePoints[v3]
                Wave.ValueVertex[4] = 0
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = 0
                Wave.IndexVertex[1] = 0
                Wave.IndexVertex[2] = IndexStart
                Wave.IndexVertex[3] = Points.IndexPoints[v3]
                Wave.IndexVertex[4] = IndexFinish
                Wave.IndexVertex[5] = 0
                # check the wave by the rules
                if WaveRules(Wave):
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 3
                    # create the third sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the fourth sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
        v3 = v3 + 1
    # the loop of unbegun and unfinished waves with the formula "4<-5>"
    v4 = 0
    while v4 <= Points.NumPoints - 1:
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure in order to know the number of symbols and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if WaveDescription[IndexWave].NumWave == 5:
                # create the object of TWave class and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "4<-5>"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = 0
                Wave.ValueVertex[2] = 0
                Wave.ValueVertex[3] = 0
                Wave.ValueVertex[4] = Points.ValuePoints[v4]
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = 0
                Wave.IndexVertex[1] = 0
                Wave.IndexVertex[2] = 0
                Wave.IndexVertex[3] = IndexStart
                Wave.IndexVertex[4] = Points.IndexPoints[v4]
                Wave.IndexVertex[5] = IndexFinish
                # check the wave by the rules
                if WaveRules(Wave):
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 4
                    # create the fourth sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the fifth sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

        v4 = v4 + 1

# +------------------------------------------------------------------+
# | The function NotStartedWaves                                          |
# +------------------------------------------------------------------+
def NotStartedWaves(ParentWave, NumWave, Node, Subwaves, Level):
    Points = TPoints()
    ParentNode = TNode()
    ChildNode = TNode()
    Wave = TWave()
    i = 0
    Pos = 0
    Start = 0
    # Put the waves, which we will be analyzing to the ListNameWave array
    #ArrayResize(ListNameWave, ArrayRange(WaveDescription, 0))
    #while (Pos != len(Subwaves) - 1):
    #    Pos = StringFind(Subwaves, ",", Start)
    #    NameWave = StringSubstr(Subwaves, Start, Pos - Start)
    #    ListNameWave[i] = NameWave
    #    i += 1
    #    Start = Pos + 1
    # Put the waves, which we will be analyzing to the ListNameWave array
    ListNameWave = [None] * len(WaveDescription)
    for part in Subwaves.split(','):
        ListNameWave[i] = part
        i += 1

    IndexStart = ParentWave.IndexVertex[NumWave - 1]
    IndexFinish = ParentWave.IndexVertex[NumWave]
    ValueStart = ParentWave.ValueVertex[NumWave - 1]
    ValueFinish = ParentWave.ValueVertex[NumWave]
    # find no less than two points on the price chart and put them into the structure Points
    # if we didn't find any, then exit the function
    if FindPoints(2, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False:
        return
    # loop the unbegun waves with the formula "4<-5"
    v5 = Points.NumPoints - 1
    v4 = v5 - 1
    while (v4 >= 0):
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure in order to know the number of its sub-waves and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if (WaveDescription[IndexWave].NumWave == 5):
                # create the object of class TWave and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "4<-5"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = 0
                Wave.ValueVertex[2] = 0
                Wave.ValueVertex[3] = 0
                Wave.ValueVertex[4] = Points.ValuePoints[v4]
                Wave.ValueVertex[5] = Points.ValuePoints[v5]
                Wave.IndexVertex[0] = 0
                Wave.IndexVertex[1] = 0
                Wave.IndexVertex[2] = 0
                Wave.IndexVertex[3] = IndexStart
                Wave.IndexVertex[4] = Points.IndexPoints[v4]
                Wave.IndexVertex[5] = Points.IndexPoints[v5]
                # check the wave by the rules
                if WaveRules(Wave) == True:
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 4
                    # create the fourth sub-wave in the wave tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create 5th sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

        v4 = v4 - 2

    # loop the unbegun waves with the formula "2<-3"
    v3 = Points.NumPoints - 1
    v2 = v3 - 1
    while (v2 >= 0):
        j = 0
        while (j <= i - 1):
            # in turn, from the ListNameWave, draw the name of the wave for analysis
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if WaveDescription[IndexWave].NumWave == 3:
                # create the object of class TWave and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "2<-3"
                Wave.ValueVertex[0] = 0
                Wave.ValueVertex[1] = 0
                Wave.ValueVertex[2] = Points.ValuePoints[v2]
                Wave.ValueVertex[3] = Points.ValuePoints[v3]
                Wave.ValueVertex[4] = 0
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = 0
                Wave.IndexVertex[1] = IndexStart
                Wave.IndexVertex[2] = Points.IndexPoints[v2]
                Wave.IndexVertex[3] = Points.IndexPoints[v3]
                Wave.IndexVertex[4] = 0
                Wave.IndexVertex[5] = 0
                # check the wave by the rules
                if WaveRules(Wave):
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 2
                    # create the second sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the third sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

        v2 = v2 - 2

    # find not less than three points on the price chart and put them into the structure Points
    # if we didn't find any, then exit the function
    if FindPoints(3, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # loop the unbegun waves with the formula "3<-4-5"
    v5 = Points.NumPoints - 1
    v4 = v5 - 1
    while (v4 >= 1):
        v3 = v4 - 1
        while (v3 >= 0):
            j = 0
            while (j <= i - 1):
                # get the name of the wave for analysis from ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if WaveDescription[IndexWave].NumWave == 5:
                    # create the object of class TWave and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "3<-4-5"
                    Wave.ValueVertex[0] = 0
                    Wave.ValueVertex[1] = 0
                    Wave.ValueVertex[2] = 0
                    Wave.ValueVertex[3] = Points.ValuePoints[v3]
                    Wave.ValueVertex[4] = Points.ValuePoints[v4]
                    Wave.ValueVertex[5] = Points.ValuePoints[v5]
                    Wave.IndexVertex[0] = 0
                    Wave.IndexVertex[1] = 0
                    Wave.IndexVertex[2] = IndexStart
                    Wave.IndexVertex[3] = Points.IndexPoints[v3]
                    Wave.IndexVertex[4] = Points.IndexPoints[v4]
                    Wave.IndexVertex[5] = Points.IndexPoints[v5]
                    # check the wave by the rules
                    if WaveRules(Wave) == True:
                        # if the wave passed the check by the rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 3
                        # create the three sub-waves in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                            Level + 1)
                        I += 1
                        # create the fourth sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the fifth sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                    # otherwise, if the wave did not pass by the rules, release the memory
                    # else delete Wave
            v3 = v3 - 2
        v4 = v4 - 2

    # the loop of the unbegun waves with the formula "1<-2-3"
    v3 = Points.NumPoints - 1
    v2 = v3 - 1
    while v2 >= 1:
        v1 = v2 - 1
        while v1 >= 0:
            j = 0
            while (j <= i - 1):
                # get the name of the wave for analysis from ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if WaveDescription[IndexWave].NumWave == 3:
                    # create the object of class TWave and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "1<-2-3"
                    Wave.ValueVertex[0] = 0
                    Wave.ValueVertex[1] = Points.ValuePoints[v1]
                    Wave.ValueVertex[2] = Points.ValuePoints[v2]
                    Wave.ValueVertex[3] = Points.ValuePoints[v3]
                    Wave.ValueVertex[4] = 0
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = IndexStart
                    Wave.IndexVertex[1] = Points.IndexPoints[v1]
                    Wave.IndexVertex[2] = Points.IndexPoints[v2]
                    Wave.IndexVertex[3] = Points.IndexPoints[v3]
                    Wave.IndexVertex[4] = 0
                    Wave.IndexVertex[5] = 0
                    # check the wave by the rules
                    if WaveRules(Wave):
                        # if the wave passed the check by the rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 1
                        # create the first sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the second sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the third sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

            v1 = v1 - 2
        v2 = v2 - 2

    # find no less than four points on the price chart and put them into the structure Points
    # if we didn't find any, then exit the function
    if (FindPoints(4, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False): return
    # the loop of unbegun waves with the formula "2<-3-4-5"
    v5 = Points.NumPoints - 1
    v4 = v5 - 1
    while v4 >= 2:
        v3 = v4 - 1
        while v3 >= 1:
            v2 = v3 - 1
            while v2 >= 0:
                j = 0
                while (j <= i - 1):
                    # in turn, from the ListNameWave, draw the name of the wave for analysis
                    NameWave = ListNameWave[j]
                    j += 1
                    # find the index of the wave in the WaveDescription structure in order to know the number of its sub-waves and their names
                    IndexWave = FindWaveInWaveDescription(NameWave)
                    if (WaveDescription[IndexWave].NumWave == 5):
                        # create the object of class TWave and fill its fields - parameters of the analyzed wave
                        Wave = TWave()
                        Wave.Name = NameWave
                        Wave.Level = Level
                        Wave.Formula = "2<-3-4-5"
                        Wave.ValueVertex[0] = 0
                        Wave.ValueVertex[1] = 0
                        Wave.ValueVertex[2] = Points.ValuePoints[v2]
                        Wave.ValueVertex[3] = Points.ValuePoints[v3]
                        Wave.ValueVertex[4] = Points.ValuePoints[v4]
                        Wave.ValueVertex[5] = Points.ValuePoints[v5]
                        Wave.IndexVertex[0] = 0
                        Wave.IndexVertex[1] = IndexStart
                        Wave.IndexVertex[2] = Points.IndexPoints[v2]
                        Wave.IndexVertex[3] = Points.IndexPoints[v3]
                        Wave.IndexVertex[4] = Points.IndexPoints[v4]
                        Wave.IndexVertex[5] = Points.IndexPoints[v5]
                        # check the wave by the rules
                        if (WaveRules(Wave) == True):
                            # if the wave passed the check by the rules, add it to the waves tree
                            ParentNode = Node.Add(NameWave, Wave)
                            I = 2
                            # create the second sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the third sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the fourth sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                              Level + 1)
                            I += 1
                            # create the fifth sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                v2 = v2 - 2
            v3 = v3 - 2
        v4 = v4 - 2

    # find no less than five points on the price chart and record it into the structure Points
    # if we didn't find any, then exit the function
    if FindPoints(5, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of unbegun waves with the formula "1<-2-3-4-5"
    v5 = Points.NumPoints - 1
    v4 = v5 - 1
    while v4 >= 3:
        v3 = v4 - 1
        while v3 >= 2:
            v2 = v3 - 1
            while v2 >= 1:
                v1 = v2 - 1
                while v1 >= 0:
                    j = 0
                    while (j <= i - 1):
                        # in turn, from the ListNameWave, draw the name of the wave for analysis
                        NameWave = ListNameWave[j]
                        j += 1
                        # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
                        IndexWave = FindWaveInWaveDescription(NameWave)
                        if WaveDescription[IndexWave].NumWave == 5:
                            # create the object of class TWave and fill its fields - parameters of the analyzed wave
                            Wave = TWave()
                            Wave.Name = NameWave
                            Wave.Level = Level
                            Wave.Formula = "1<-2-3-4-5"
                            Wave.ValueVertex[0] = 0
                            Wave.ValueVertex[1] = Points.ValuePoints[v1]
                            Wave.ValueVertex[2] = Points.ValuePoints[v2]
                            Wave.ValueVertex[3] = Points.ValuePoints[v3]
                            Wave.ValueVertex[4] = Points.ValuePoints[v4]
                            Wave.ValueVertex[5] = Points.ValuePoints[v5]
                            Wave.IndexVertex[0] = IndexStart
                            Wave.IndexVertex[1] = Points.IndexPoints[v1]
                            Wave.IndexVertex[2] = Points.IndexPoints[v2]
                            Wave.IndexVertex[3] = Points.IndexPoints[v3]
                            Wave.IndexVertex[4] = Points.IndexPoints[v4]
                            Wave.IndexVertex[5] = Points.IndexPoints[v5]
                            # check the wave by the rules
                            if WaveRules(Wave) == True:
                                # if the wave passed the check by the rules, add it to the waves tree
                                ParentNode = Node.Add(NameWave, Wave)
                                I = 1
                                # create the first sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    NotStartedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                    Level + 1)
                                I += 1
                                # create the second sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                  Level + 1)
                                I += 1
                                # create the third sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                  Level + 1)
                                I += 1
                                # create the fourth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                  Level + 1)
                                I += 1
                                # create the fifth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the chart, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                  Level + 1)

                    v1 = v1 - 2
                v2 = v2 - 2
            v3 = v3 - 2
        v4 = v4 - 2


# +------------------------------------------------------------------+
# | The function FinishedWaves                                         |
# +------------------------------------------------------------------+
def NotFinishedWaves(ParentWave, NumWave, Node, Subwaves, Level):
    Points = TPoints()
    i = 0
    Pos = 0
    Start = 0
    # we put the waves, which we will be analyzing in the array ListNameWaveg
    #ArrayResize(ListNameWave, ArrayRange(WaveDescription, 0))
    #while (Pos != len(Subwaves) - 1):
    #    Pos = StringFind(Subwaves, ",", Start)
    #    NameWave = StringSubstr(Subwaves, Start, Pos - Start)
    #    ListNameWave[i] = NameWave
    #    i += 1
    #    Start = Pos + 1
    # Put the waves, which we will be analyzing to the ListNameWave array
    ListNameWave = [None] * len(WaveDescriotion)
    for part in Subwaves.split(','):
        ListNameWave[i] = part
        i += 1

    IndexStart = ParentWave.IndexVertex[NumWave - 1]
    IndexFinish = ParentWave.IndexVertex[NumWave]
    ValueStart = ParentWave.ValueVertex[NumWave - 1]
    ValueFinish = ParentWave.ValueVertex[NumWave]
    # find not less than two points on the price chart and record it into the structure Points
    # if we didn't find any, then exit the function
    if FindPoints(2, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of unfinished waves with the formula "1-2>"
    v0 = 0
    v1 = v0 + 1
    while (v1 <= Points.NumPoints - 1):
        j = 0
        while (j <= i - 1):
            # get the name of the wave for analysis from the ListNameWave
            NameWave = ListNameWave[j]
            j += 1
            # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
            IndexWave = FindWaveInWaveDescription(NameWave)
            if ((WaveDescription[IndexWave].NumWave == 5) or (WaveDescription[IndexWave].NumWave == 3)):
                # create the object of TWave class and fill its fields - parameters of the analyzed wave
                Wave = TWave()
                Wave.Name = NameWave
                Wave.Level = Level
                Wave.Formula = "1-2>"
                Wave.ValueVertex[0] = Points.ValuePoints[v0]
                Wave.ValueVertex[1] = Points.ValuePoints[v1]
                Wave.ValueVertex[2] = 0
                Wave.ValueVertex[3] = 0
                Wave.ValueVertex[4] = 0
                Wave.ValueVertex[5] = 0
                Wave.IndexVertex[0] = Points.IndexPoints[v0]
                Wave.IndexVertex[1] = Points.IndexPoints[v1]
                Wave.IndexVertex[2] = IndexFinish
                Wave.IndexVertex[3] = 0
                Wave.IndexVertex[4] = 0
                Wave.IndexVertex[5] = 0
                # check the wave by the rules
                if (WaveRules(Wave) == True):
                    # if the wave passed the check by the rules, add it to the waves tree
                    ParentNode = Node.Add(NameWave, Wave)
                    I = 1
                    # create the first sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                    I += 1
                    # create the second sub-wave in the waves tree
                    ChildNode = ParentNode.Add(str(I))
                    # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                    if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                        NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

        v1 = v1 + 2

    # find no less than three points on the price chart and put it into the Points structure
    # if none were found, then exit the function
    if FindPoints(3, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of unfinished waves with the formula "1-2-3>"
    v0 = 0
    v1 = v0 + 1
    while (v1 <= Points.NumPoints - 2):
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 1):
            j = 0
            while (j <= i - 1):
                # get the name of the wave for analysis from ListNameWave
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the WaveDescription structure in order to know the number of sub-waves and their names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if ((WaveDescription[IndexWave].NumWave == 5) or (WaveDescription[IndexWave].NumWave == 3)):
                    # create the object of TWave class and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Level = Level
                    Wave.Formula = "1-2-3>"
                    Wave.ValueVertex[0] = Points.ValuePoints[v0]
                    Wave.ValueVertex[1] = Points.ValuePoints[v1]
                    Wave.ValueVertex[2] = Points.ValuePoints[v2]
                    Wave.ValueVertex[3] = 0
                    Wave.ValueVertex[4] = 0
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = Points.IndexPoints[v0]
                    Wave.IndexVertex[1] = Points.IndexPoints[v1]
                    Wave.IndexVertex[2] = Points.IndexPoints[v2]
                    Wave.IndexVertex[3] = IndexFinish
                    Wave.IndexVertex[4] = 0
                    Wave.IndexVertex[5] = 0
                    # check the wave by the rules
                    if WaveRules(Wave) == True:
                        # if the wave passed the check by the rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 1
                        # create the first sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the second sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the third sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, of the corresponding third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

            v2 = v2 + 2
        v1 = v1 + 2

    # find no less than four points on the price chart and record it into the Points structure
    # if none were found, then exit the function
    if (FindPoints(4, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False): return
    # the loop of unfinished waves with the formula "1-2-3-4>"
    v0 = 0
    v1 = v0 + 1
    while (v1 <= Points.NumPoints - 3):
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 2):
            v3 = v2 + 1
            while (v3 <= Points.NumPoints - 1):
                j = 0
                while (j <= i - 1):
                    # get the name of the wave for analysis from ListNameWave
                    NameWave = ListNameWave[j]
                    j += 1
                    # find the index of the wave in WaveDescription structure in order to know the number of sub-waves and the names
                    IndexWave = FindWaveInWaveDescription(NameWave)
                    if (WaveDescription[IndexWave].NumWave == 5):
                        # create the object of TWave class and fill its fields - parameters of the analyzed wave
                        Wave = TWave()
                        Wave.Name = NameWave
                        Wave.Level = Level
                        Wave.Formula = "1-2-3-4>"
                        Wave.ValueVertex[0] = Points.ValuePoints[v0]
                        Wave.ValueVertex[1] = Points.ValuePoints[v1]
                        Wave.ValueVertex[2] = Points.ValuePoints[v2]
                        Wave.ValueVertex[3] = Points.ValuePoints[v3]
                        Wave.ValueVertex[4] = 0
                        Wave.ValueVertex[5] = 0
                        Wave.IndexVertex[0] = Points.IndexPoints[v0]
                        Wave.IndexVertex[1] = Points.IndexPoints[v1]
                        Wave.IndexVertex[2] = Points.IndexPoints[v2]
                        Wave.IndexVertex[3] = Points.IndexPoints[v3]
                        Wave.IndexVertex[4] = IndexFinish
                        Wave.IndexVertex[5] = 0
                        # check the wave by the rules
                        if (WaveRules(Wave) == True):
                            # if the wave passed the check for the rules, add it to the waves tree
                            ParentNode = Node.Add(NameWave, Wave)
                            I = 1
                            # create the first sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the second sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the third sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                            I += 1
                            # create the fourth sub-wave in the waves tree
                            ChildNode = ParentNode.Add(str(I))
                            # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                            if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                v3 = v3 + 2
            v2 = v2 + 2
        v1 = v1 + 2

    # find no less than five points on the price chart and put them into the structure Points
    # if none were found, exit the function
    if (FindPoints(5, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False): return
    # the loop of unfinished waves with the formula "1-2-3-4-5>"
    v0 = 0
    v1 = v0 + 1
    while (v1 <= Points.NumPoints - 4):
        v2 = v1 + 1
        while (v2 <= Points.NumPoints - 3):
            v3 = v2 + 1
            while (v3 <= Points.NumPoints - 2):
                v4 = v3 + 1
                while (v4 <= Points.NumPoints - 1):
                    j = 0
                    while (j <= i - 1):
                        # get the name of the wave for analysis from ListNameWave
                        NameWave = ListNameWave[j]
                        j += 1
                        # find the index of the wave in the WaveDescription structure in order to know the number of its sub-waves and their names
                        IndexWave = FindWaveInWaveDescription(NameWave)
                        if (WaveDescription[IndexWave].NumWave == 5):
                            # create the object of TWave class and fill its fields - parameters of the analyzed wave
                            Wave = TWave()
                            Wave.Name = NameWave
                            Wave.Level = Level
                            Wave.Formula = "1-2-3-4-5>"
                            Wave.ValueVertex[0] = Points.ValuePoints[v0]
                            Wave.ValueVertex[1] = Points.ValuePoints[v1]
                            Wave.ValueVertex[2] = Points.ValuePoints[v2]
                            Wave.ValueVertex[3] = Points.ValuePoints[v3]
                            Wave.ValueVertex[4] = Points.ValuePoints[v4]
                            Wave.ValueVertex[5] = 0
                            Wave.IndexVertex[0] = Points.IndexPoints[v0]
                            Wave.IndexVertex[1] = Points.IndexPoints[v1]
                            Wave.IndexVertex[2] = Points.IndexPoints[v2]
                            Wave.IndexVertex[3] = Points.IndexPoints[v3]
                            Wave.IndexVertex[4] = Points.IndexPoints[v4]
                            Wave.IndexVertex[5] = IndexFinish
                            # check the wave by the rules
                            if WaveRules(Wave):
                                # if the wave passed the check by the rules, add it to the waves tree
                                ParentNode = Node.Add(NameWave, Wave)
                                I = 1
                                # create the first sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the second sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the third sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the fourth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the fifth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    NotFinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I],
                                                     Level + 1)

                    v4 = v4 + 2
                v3 = v3 + 2
            v2 = v2 + 2
        v1 = v1 + 2


# +------------------------------------------------------------------+
# | The FinishedWaves function                                       |
# +------------------------------------------------------------------+
def FinishedWaves(ParentWave, NumWave, Node, Subwaves, Level):
    Points = TPoints()
    i = 0
    Pos = 0
    Start = 0
    # Put the waves, which we will be analyzing to the ListNameWave array
    #ArrayResize(ListNameWave, ArrayRange(WaveDescription, 0))
    #while (Pos != len(Subwaves) - 1):
    #    Pos = StringFind(Subwaves, ",", Start)
    #    NameWave = StringSubstr(Subwaves, Start, Pos - Start)
    #    ListNameWave[i] = NameWave
    #    i += 1
    #    Start = Pos + 1

    # Put the waves, which we will be analyzing to the ListNameWave array
    ListNameWave = [None] * len(WaveDescriotion)
    for part in Subwaves.split(','):
        ListNameWave[i] = part
        i += 1

    IndexStart = ParentWave.IndexVertex[NumWave - 1]
    IndexFinish = ParentWave.IndexVertex[NumWave]
    ValueStart = ParentWave.ValueVertex[NumWave - 1]
    ValueFinish = ParentWave.ValueVertex[NumWave]
    # find no less than four points on the price chart and put them into the structure Points
    # if none were found, then exit the function
    if FindPoints(4, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False: return
    # the loop of complete waves with the formula "1-2-3"
    v0 = 0
    v1 = 1
    v3 = Points.NumPoints - 1
    while (v1 <= v3 - 2):
        v2 = v1 + 1
        while (v2 <= v3 - 1):
            j = 0
            while (j <= i - 1):
                # in tuen, from ListNameWave, draw the name of the wave for analysis
                NameWave = ListNameWave[j]
                j += 1
                # find the index of the wave in the structure WaveDescription in order to know the number of sub-waves and its names
                IndexWave = FindWaveInWaveDescription(NameWave)
                if (WaveDescription[IndexWave].NumWave == 3):
                    # create the object of class TWave and fill its fields - parameters of the analyzed wave
                    Wave = TWave()
                    Wave.Name = NameWave
                    Wave.Formula = "1-2-3"
                    Wave.Level = Level
                    Wave.ValueVertex[0] = Points.ValuePoints[v0]
                    Wave.ValueVertex[1] = Points.ValuePoints[v1]
                    Wave.ValueVertex[2] = Points.ValuePoints[v2]
                    Wave.ValueVertex[3] = Points.ValuePoints[v3]
                    Wave.ValueVertex[4] = 0
                    Wave.ValueVertex[5] = 0
                    Wave.IndexVertex[0] = Points.IndexPoints[v0]
                    Wave.IndexVertex[1] = Points.IndexPoints[v1]
                    Wave.IndexVertex[2] = Points.IndexPoints[v2]
                    Wave.IndexVertex[3] = Points.IndexPoints[v3]
                    Wave.IndexVertex[4] = 0
                    Wave.IndexVertex[5] = 0
                    # check the wave by the rules
                    if WaveRules(Wave):
                        # if the wave passed the check by the rules, add it to the waves tree
                        ParentNode = Node.Add(NameWave, Wave)
                        I = 1
                        # create the first sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(i))
                        # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the second sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(i))
                        # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                        I += 1
                        # create the third sub-wave in the waves tree
                        ChildNode = ParentNode.Add(str(I))
                        # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                        if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                            FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

            v2 = v2 + 2
        v1 = v1 + 2

    # find no less than six points on the price chart and put them into the structure Points
    # if none were found, then exit the function
    if (FindPoints(6, IndexStart, IndexFinish, ValueStart, ValueFinish, Points) == False): return
    # the loop of complete waves with the formula "1-2-3-4-5"
    v0 = 0
    v1 = 1
    v5 = Points.NumPoints - 1
    while (v1 <= v5 - 4):
        v2 = v1 + 1
        while (v2 <= v5 - 3):
            v3 = v2 + 1
            while (v3 <= v5 - 2):
                v4 = v3 + 1
                while (v4 <= v5 - 1):
                    j = 0
                    while (j <= i - 1):
                        # get the name of the wave for analysis from ListNameWave
                        NameWave = ListNameWave[j]
                        j += 1
                        # find the index of the wave in the WaveDescription structure in order to know the number of its sub-waves and their names
                        IndexWave = FindWaveInWaveDescription(NameWave)
                        if (WaveDescription[IndexWave].NumWave == 5):
                            # create the object of class TWave and fill its fields - parameters of the analyzed wave
                            Wave = TWave()
                            Wave.Name = NameWave
                            Wave.Level = Level
                            Wave.Formula = "1-2-3-4-5"
                            Wave.ValueVertex[0] = Points.ValuePoints[v0]
                            Wave.ValueVertex[1] = Points.ValuePoints[v1]
                            Wave.ValueVertex[2] = Points.ValuePoints[v2]
                            Wave.ValueVertex[3] = Points.ValuePoints[v3]
                            Wave.ValueVertex[4] = Points.ValuePoints[v4]
                            Wave.ValueVertex[5] = Points.ValuePoints[v5]
                            Wave.IndexVertex[0] = Points.IndexPoints[v0]
                            Wave.IndexVertex[1] = Points.IndexPoints[v1]
                            Wave.IndexVertex[2] = Points.IndexPoints[v2]
                            Wave.IndexVertex[3] = Points.IndexPoints[v3]
                            Wave.IndexVertex[4] = Points.IndexPoints[v4]
                            Wave.IndexVertex[5] = Points.IndexPoints[v5]
                            # check the wave by the rules
                            if (WaveRules(Wave) == True):
                                # if the wave passed the check by the rules, add it to the waves tree
                                ParentNode = Node.Add(NameWave, Wave)
                                I = 1
                                # create the first sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the first sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the second sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the second sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the third sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the third sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the fourth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fourth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)
                                I += 1
                                # create the fifth sub-wave in the waves tree
                                ChildNode = ParentNode.Add(str(I))
                                # if the interval of the chart, corresponding to the fifth sub-wave, has not been analyzed, then analyze it
                                if Already(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I]) == False:
                                    FinishedWaves(Wave, I, ChildNode, WaveDescription[IndexWave].Subwaves[I], Level + 1)

                    v4 = v4 + 2
                v3 = v3 + 2
            v2 = v2 + 2
        v1 = v1 + 2


def Already(Wave, NumWave, Node, Subwaves, NodeInfoArray):
    # obtain the necessary parameters of the wave or the group of waves
    IndexStart = Wave.IndexVertex[NumWave - 1]
    IndexFinish = Wave.IndexVertex[NumWave]
    ValueStart = Wave.ValueVertex[NumWave - 1]
    ValueFinish = Wave.ValueVertex[NumWave]
    # in the loop, proceed the array NodeInfoArray for the search of the marked-up section of the chart
    for i in range(len(NodeInfoArray) - 1, 0, -1):
        NodeInfo = NodeInfoArray[i]
        # if the required section has already been marked-up
        if (NodeInfo.Subwaves == Subwaves and (NodeInfo.ValueStart == ValueStart) and
                (NodeInfo.ValueFinish == ValueFinish) and (NodeInfo.IndexStart == IndexStart) and
                (NodeInfo.IndexFinish == IndexFinish)):
            # add the child nodes of the found node into the child nodes of the new node
            for j in range(0, len(NodeInfo.Node.Child)):
                Node.Child.append(NodeInfo.Node.Child[j])
            return True

    # if the interval has not been marked-up earlier, then record its data into the array NodeInfoArray
    NodeInfo = TNodeInfo()
    NodeInfo.IndexStart = IndexStart
    NodeInfo.IndexFinish = IndexFinish
    NodeInfo.ValueStart = ValueStart
    NodeInfo.ValueFinish = ValueFinish
    NodeInfo.Subwaves = Subwaves
    NodeInfo.Node = Node
    NodeInfoArray.Add(NodeInfo)
    return False
