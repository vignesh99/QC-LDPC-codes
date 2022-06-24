'''
This file has all the functions used for generating
the animations
'''
from pylab import *
from manim import *
import networkx as nx
from manimnx import manimnx as mnx

'''
Generic functions used across animations
'''

def genshiftedIM(cshift,N=3) :
    '''
    Obtain shifted identity matrix in manim format

    Input :
    cshift - circular shift index
    N - size of square matrix

    Output :
    manimIM - shifted identity matrix
    npIM - corresponding numpy array
    '''
    #Null matrix when shift = -1
    if cshift == -1 :
        manimIM = (Matrix((np.zeros((N,N)).astype("int")).astype("str"),width=0.2,height=0.2)
               .scale(0.5)
               )
        npIM = np.zeros((N,N))
    else :
        manimIM = (Matrix((np.roll(np.identity(N),cshift,axis=1).astype("int")).astype("str"),width=0.2,height=0.2)
               .scale(0.5)
               )
        npIM = np.roll(np.identity(N),cshift,axis=1)

    return manimIM,npIM

###################################################################################################################
###################################################################################################################
def VNstoCN(shiftarr,Z=3) :
    '''
    This gives the VNs connecting to each CN in the
    row-wise order and required format
    
    Input :
    shiftarr - array containing expansion matrices of 
shift values
    
    Output :
    cxnstr - string containing the VN-CN connections
        Eg : "1-3,4-6,3-5"  
    '''
    #Obtain the concatenated array of shift expansions
    stackarr = np.hstack(shiftarr)
    onesind = np.where(stackarr!=0)
    strcnxlist = []
    for i in range(Z) :
        #Find nz col of each row & combine it to str
        indstrlist = list(onesind[1][np.where(onesind[0] == i)[0]].astype("str"))
        #Add dashes to distinguish 2 digit numbers
        strcnxlist.append('-'.join(indstrlist))

    #Combine all cnxs using ','
    cnxstr = ','.join(strcnxlist)
    return cnxstr

###################################################################################################################
###################################################################################################################
def tg_edge(ed,G) :
    '''
    Define edge and its properties related to
    that edge
    modified from : https://github.com/rajatvd/FactorGraphs/blob/ab5c0423d599b54371636edc041c062f09ed7109/fg_anim.py#L77

    Input :
    ed - nodes connected to the current edge
    G - factor graph (MultiDigraph)

    Output :
    edge - bezier curve(?) VMobject for the edge
    '''
    node1 = G.nodes[ed[0]]
    node2 = G.nodes[ed[1]]
    x1, y1 = node1['pos']
    x2, y2 = node2['pos']
    start = x1*RIGHT + y1*UP
    end = x2*RIGHT + y2*UP

    pnts = [x*RIGHT + y*UP for x, y in G.edges[ed].get('points', [])]

    edge = VMobject(color=BLACK)
    edge.set_points_smoothly([start, *pnts, end])

    return edge

###################################################################################################################
###################################################################################################################
def add_brack(mobj,Zval=2,v_buff=0.25,h_buff=0.25):
    '''
    Add brackets around a mobject

    Input : 
    mobj - any manim object
    Zval - required height of the bracket
    v_buff - vertical additional height
    h_buff - horizontal additional height

    Output :
    brack - brackets around the input object
    '''
    # Height per row of LaTeX array with default settings
    BRACKET_HEIGHT = 0.5977

    n = int((Zval) / BRACKET_HEIGHT) + 1
    empty_tex_array = "".join(
    [
        r"\begin{array}{c}",
        *n * [r"\quad \\"],
        r"\end{array}",
    ]
    )
    tex_left = "".join(
        [
            r"\left" + "[",
            empty_tex_array,
            r"\right.",
        ]
    )
    tex_right = "".join(
        [
            r"\left.",
            empty_tex_array,
            r"\right" + "]",
        ]
    )
    l_bracket = MathTex(tex_left, color=BLACK)
    r_bracket = MathTex(tex_right, color=BLACK)
        
    #Placement
    l_bracket.next_to(mobj, LEFT, h_buff)
    r_bracket.next_to(mobj, RIGHT, h_buff)
    
    return VGroup(l_bracket, r_bracket)

###################################################################################################################
###################################################################################################################
def tg_node(n,G,h=0.6,w=0.6) :
    '''
    Define the node and its properties
    modified from : https://github.com/rajatvd/FactorGraphs/blob/ab5c0423d599b54371636edc041c062f09ed7109/fg_anim.py#L34

    Input :
    n - node key
    G - factor graph
    h - height
    w - width

    Output :
    grp - manim node object
    '''
    node = G.nodes[n]
    type_to_shape = {
        'variablenode': Circle,
        'checknode': Rectangle
    }

    def node_color(node_dict):
        if node_dict['type'] == 'checknode':
            return GREEN
        return PURPLE_B

    def node_name(n,node_dict) :
        if node_dict['type'] == 'checknode' :
            return  MathTex("C_{",n,"}",height=0.3, color=BLACK)
            #return TexMobject(n, color=BLACK)
        return MathTex("V_{",n,"}",height=0.27, color=BLACK)
        #return TexMobject(n, color=BLACK)

    bg = type_to_shape[node['type']](color=BLACK, fill_color=node_color(node),
                                     fill_opacity=1, radius=0.25,
                                     height=h, width=w)
    x, y = node['pos']
    grp = VGroup(bg, node_name(n,node))
    grp.move_to(x*RIGHT + y*UP)
    return grp

###################################################################################################################
###################################################################################################################
def tanner_graph(cnodes,N,vnodes) :
    '''
    The factor graph with check nodes and variable
    nodes. Each block(CN-VN) will have two cases for 
    connection, either zero/non-zero block and no. of 
    edges will be decided accordingly.

    Input :
    cnodes - list of check node names
    N - no. of variable nodes
    vnodes - grouped set of variable node connected
to each check node

    Output :
    tg - the required tanner graph
    '''
    tg = nx.MultiGraph()
    for cn in cnodes :  #add type attribute
        tg.add_node(cn,type='checknode')

    #Modify according to i/p
    allvnodes = (np.arange(N).astype("int")).astype("str")
    for vn in allvnodes : 
        tg.add_node(vn,type='variablenode')

    #Obtain CN-VN edges
    vncxns = vnodes.split(",")
    for cn,vns in zip(cnodes,vncxns) :
        for i,vn in enumerate(vns.split('-')) :
            tg.add_edge(cn,vn,axis=i)  #Why use axis?

    return tg

###################################################################################################################
'''
Animation specific functions
'''
###################################################################################################################
def tg_node_LDPC(n,G,h=0.8,w=0.8) :
    '''
    Define the node and its properties with Tx node

    Input :
    n - node key
    G - factor graph
    h - height
    w - width

    Output :
    grp - manim node object
    '''
    node = G.nodes[n]
    type_to_shape = {
        'variablenode': Circle,
        'checknode': Rectangle,
        'qnode':Circle
    }

    def node_color(node_dict):
        if node_dict['type'] == 'checknode':
            return GREEN_D
        elif node_dict['type'] == 'qnode':
            return RED_D
        return PURPLE_B

    def node_name(n,node_dict) :
        if node_dict['type'] == 'checknode' :
            return  MathTex(node_dict['name'],color=node['txtcolor']).set_opacity(0)
        #Offset the value from G to the 1st letter of QNs
        elif node_dict['type'] == 'qnode' :
            return  MathTex(node_dict['name'],height=0.3, color=BLACK)
        return MathTex(node_dict['name'],height=0.3, color=node['txtcolor'])

    bg = type_to_shape[node['type']](color=BLACK, fill_color=node_color(node),
                                     fill_opacity=1, radius=0.25,
                                     height=h, width=w)
    x, y = node['pos']
    grp = VGroup(bg, node_name(n,node))
    grp.move_to(x*RIGHT + y*UP)
    return grp

###################################################################################################################
###################################################################################################################
def tanner_graph_LDPC(cnodes,N,vnodes,qnodes,cnlabels,vnlabels,qnlabels) :
    '''
    The factor graph with check nodes and variable
    nodes. Each block(CN-VN) will have two cases for 
    connection, either zero/non-zero block and no. of 
    edges will be decided accordingly.
    Tx nodes are connected to this factor graph

    Input :
    cnodes - list of check node names
    N - no. of variable nodes
    vnodes - grouped set of variable nodes connected
to each check node
    qnodes - grouped set of transmitted nodes connected
to each variable node
    cnlabels - list of names displayed on check nodes
    vnlabels - list of names displayed on variable nodes
    qnlabels - list of names displayed on tx nodes

    Output :
    tg - the required tanner graph
    '''
    tg = nx.MultiDiGraph()
    for cn in range(len(cnodes)) :  #add type attribute
        tg.add_node(cnodes[cn],type='checknode',name=cnlabels[cn],txtcolor=GREEN_D)
        
    #Modify according to i/p
    allvnodes = (np.arange(N).astype("int")).astype("str")
    for vn in range(len(allvnodes)) :
        if vnlabels[vn] == "." :
            colorval = PURPLE_B
        else :
            colorval = BLACK
        tg.add_node(allvnodes[vn],type='variablenode',name=vnlabels[vn],txtcolor=colorval)
        
    for qn in range(len(qnodes)) :  #add type attribute
        tg.add_node(qnodes[qn],type='qnode',name=qnlabels[qn],txtcolor=BLACK)
        
    #Obtain CN-VN edges
    vncxns = vnodes.split(",")
    for cn,vns in zip(cnodes,vncxns) :
        for i,vn in enumerate(vns.split('-')) :
            tg.add_edge(cn,vn,axis=i)
            tg.add_edge(vn,cn,axis=i)

    #Add VN-Q edges
    for vn in allvnodes :
        tg.add_edge(vn,qnodes[int(vn)])
        tg.add_edge(qnodes[int(vn)],vn)

    return tg

###################################################################################################################
###################################################################################################################
def tg_node_OUTLOOK(n,G,h=0.8,w=0.8) :
    '''
    Define the node and its properties with Tx node

    Input :
    n - node key
    G - factor graph
    h - height
    w - width

    Output :
    grp - manim node object
    '''
    node = G.nodes[n]
    type_to_shape = {
        'variablenode': Circle,
        'checknode': Rectangle,
        'qnode':Circle
    }

    def node_color(node_dict):
        if node_dict['type'] == 'checknode':
            return GREEN_D
        elif node_dict['type'] == 'qnode':
            return RED_D
        return PURPLE_B

    def node_name(n,node_dict) :
        if node_dict['type'] == 'checknode' :
            return  MathTex("C_{",n,"}", color=BLACK)
        #Offset the value from G to the 1st letter of QNs
        elif node_dict['type'] == 'qnode' :
            return  MathTex("Q_{",str(ord(n)-ord('G')),"}",height=0.3, color=BLACK)
        return MathTex("V_{",n,"}",height=0.3, color=BLACK)

    bg = type_to_shape[node['type']](color=BLACK, fill_color=node_color(node),
                                     fill_opacity=1, radius=0.25,
                                     height=h, width=w)
    x, y = node['pos']
    grp = VGroup(bg, node_name(n,node))
    grp.move_to(x*RIGHT + y*UP)
    return grp

###################################################################################################################
###################################################################################################################
def tanner_graph_OUTLOOK(cnodes,N,vnodes,qnodes) :
    '''
    The factor graph with check nodes and variable
    nodes. Each block(CN-VN) will have two cases for 
    connection, either zero/non-zero block and no. of 
    edges will be decided accordingly.
    Memory nodes are connected to this factor graph

    Input :
    cnodes - list of check node names
    N - no. of variable nodes
    vnodes - grouped set of variable nodes connected
to each check node
    qnodes - grouped set of memory nodes connected
to each variable node

    Output :
    tg - the required tanner graph
    '''
    tg = nx.MultiDiGraph()
    for cn in cnodes :  #add type attribute
        tg.add_node(cn,type='checknode')

    #Modify according to i/p
    allvnodes = (np.arange(N).astype("int")).astype("str")
    for vn in allvnodes : 
        tg.add_node(vn,type='variablenode')

    for qn in qnodes :  #add type attribute
        tg.add_node(qn,type='qnode')

    #Obtain CN-VN edges
    vncxns = vnodes.split(",")
    for cn,vns in zip(cnodes,vncxns) :
        for i,vn in enumerate(vns.split('-')) :
            tg.add_edge(cn,vn,axis=i)
            tg.add_edge(vn,cn,axis=i)

    #Add VN-Q edges
    for vn in allvnodes :
        tg.add_edge(vn,qnodes[int(vn)])
        tg.add_edge(qnodes[int(vn)],vn)

    return tg

###################################################################################################################
###################################################################################################################
def tg_node_OMS(n,G,h=0.8,w=0.8) :
    '''
    Define the node and its properties with Tx node

    Input :
    n - node key
    G - factor graph
    h - height
    w - width

    Output :
    grp - manim node object
    '''
    node = G.nodes[n]
    type_to_shape = {
        'variablenode': Circle,
        'checknode': Rectangle,
        'qnode':Circle,
        'inode':Dot
    }

    def node_color(node_dict):
        if node_dict['type'] == 'checknode':
            return GREEN_D
        elif node_dict['type'] == 'qnode':
            return RED_D
        elif node_dict['type'] == 'inode':
            return DARK_BROWN
        return PURPLE_B

    def node_name(n,node_dict) :
        if node_dict['type'] == 'checknode' :
            return  MathTex("C_{",n,"}", color=BLACK)
        #Offset the value from G to the 1st letter of QNs
        elif node_dict['type'] == 'qnode' :
            return  MathTex("Q_{",str(ord(n)-ord('G')),"}",height=0.3, color=BLACK)
        elif node_dict['type'] == 'inode' :
            return  MathTex("",height=0.01, color=DARK_BROWN)
        return MathTex("V_{",n,"}",height=0.3, color=BLACK)

    bg = type_to_shape[node['type']](color=BLACK, fill_color=node_color(node),
                                     fill_opacity=1, radius=0.25,
                                     height=h, width=w)
    x, y = node['pos']
    grp = VGroup(bg, node_name(n,node))
    grp.move_to(x*RIGHT + y*UP)
    return grp

###################################################################################################################
###################################################################################################################
def tanner_graph_OMS(cnodes,N,vnodes,qnodes,inodes) :
    '''
    The factor graph with check nodes and variable
    nodes. Each block(CN-VN) will have two cases for 
    connection, either zero/non-zero block and no. of 
    edges will be decided accordingly.
    Memory and input nodes are connected to this factor graph

    Input :
    cnodes - list of check node names
    N - no. of variable nodes
    vnodes - grouped set of variable nodes connected
to each check node
    qnodes - grouped set of memory nodes connected
to each variable node
    inodes - grouped set of input nodes connected
to each variable node

    Output :
    tg - the required tanner graph
    '''
    tg = nx.MultiDiGraph()
    for cn in cnodes :  #add type attribute
        tg.add_node(cn,type='checknode')

    #Modify according to i/p
    allvnodes = (np.arange(N).astype("int")).astype("str")
    for vn in allvnodes : 
        tg.add_node(vn,type='variablenode')

    for qn in qnodes :  #add type attribute
        tg.add_node(qn,type='qnode')
    for ind in inodes :  #add type attribute
        tg.add_node(ind,type='inode')

    #Obtain CN-VN edges
    vncxns = vnodes.split(",")
    for cn,vns in zip(cnodes,vncxns) :
        for i,vn in enumerate(vns.split('-')) :
            tg.add_edge(cn,vn,axis=i)
            tg.add_edge(vn,cn,axis=i)

    #Add VN-QN edges
    for vn in allvnodes :
        tg.add_edge(vn,qnodes[int(vn)])
        tg.add_edge(qnodes[int(vn)],vn)

    #Add QN-IN edges
    for vn in allvnodes :
        tg.add_edge(inodes[int(vn)],qnodes[int(vn)])
        tg.add_edge(qnodes[int(vn)],inodes[int(vn)])
        
    return tg

