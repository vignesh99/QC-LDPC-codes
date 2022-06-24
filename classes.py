'''
Contains all the classes used to obtain the 
animations
'''
from pylab import *
from manim import *
import networkx as nx
from manimnx import manimnx as mnx
from functions import *

#################################################################################################################
'''
Animation 1 : LDPC decoding
'''
#################################################################################################################
class ErasureLDPC(Scene) :
    '''
    Tanner graph of LDPC code passed through
    a binary erasure channel
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 2 #No. of cnxns leaving from CN

        #Tanner graph initialization
        CNnames = ['A','B','C','D']
        VNnames = ['0', '1', '2', '3', '4', '5']
        QNnames = ['G','H','I','J','K','L']
        
        CNlabels = ['.','.','.','.']
        VNlabels = ['1','.','0','.','.','.']
        QNlabels = ['1','0','0','1','0','1']
        CNVNedgecxns = "0-3,2-4,3-5,1-4"
        
        tg = tanner_graph_LDPC(CNnames,len(VNnames),CNVNedgecxns,QNnames,CNlabels,VNlabels,QNlabels)
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5),
                   'yCN4' : np.arange(1.8,-2,-1.2),
                   'yVN6' : np.arange(2.5,-3,-1)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
        elif len(CNnames) == 4 and len(VNnames) == 6 :
            yCN = '4'
            yVN = '6'
            
        #CN coordinates
        xCN = -4
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = xCN
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        xVN = 1
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = xVN
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)
        
        #QN coordinates
        xQN = 5
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = xQN
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',QNnames , pos, tg)
        

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node_LDPC,tg_edge)
        
        #Add to make edges go behind variables
        self.add_foreground_mobjects(*mtg.nodes.values())

        #Begin fade animation
        CNVNgroups = []
        #Obtain group for animation along edge and reverse
        edgeCNVNgroups = []
        revCNVNgroups = []
        CNgroups = []
        VNgroups = []
        NZcumsum = [0]

        #Create all node groups for box
        allQNgroups = VGroup()
        allVNgroups = VGroup()
        allCNgroups = VGroup()
        #Create groups to handle together
        for i in range(len(QNnames)) :
            allQNgroups.add(mtg.nodes[tg.nodes[QNnames[i]]['mob_id']])
            allVNgroups.add(mtg.nodes[tg.nodes[VNnames[i]]['mob_id']])
        for i in range(len(CNnames)) :
            allCNgroups.add(mtg.nodes[tg.nodes[CNnames[i]]['mob_id']])

        #Fade all nodes
        allNodes = VGroup()
        for i in range(len(mtg.nodes)) :
            allNodes.add(mtg.nodes[i])
        allNodes.set_opacity(0)
        #Add Q-VN edges
        QVNgroups = VGroup()
        for qnd in QNnames :
            for ng in tg.neighbors(qnd) :
                if tg.nodes[ng]['type'] == 'variablenode' :
                    e = (qnd,ng,0)
                    QVNgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(QVNgroups.set_opacity(1))
        
        #Make all QNs, VNs visible
        allQNgroups.set_opacity(1)
        #Add channel
        rectChannel = Rectangle(height=6, width=2, fill_color=YELLOW,fill_opacity=1, stroke_color=YELLOW)
        txtCh = Text(" Binary\n Erasure\n Channel",color=BLACK).scale(0.4)
        rectChannel.move_to(3*RIGHT)
        txtCh.move_to(3*RIGHT)
        self.add_foreground_mobjects(txtCh)
        self.add(rectChannel)
        self.add(txtCh)
        #Add signal label
        txtTx = Text("Transmitted bits",color=BLACK).scale(0.4)
        txtTx.move_to(5*RIGHT+3.75*UP)
        self.add(txtTx)
        txtRx = Text("Received bits",color=BLACK).scale(0.4)
        txtRx.move_to(1*RIGHT+3.75*UP)
        self.add(txtRx)
        txtSPC = Text("SPC constraints",color=BLACK).scale(0.4)
        txtSPC.move_to(-4*RIGHT+3.75*UP)
        self.add(txtSPC)
        
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(YELLOW))
        #Send message
        self.play(*[MoveAlongPath(msg[j],QVNgroups[j]) for j in range(len(QNnames))],run_time=2)
        self.play(*[Transform(msg[j],allVNgroups[j].set_opacity(1)) for j in range(len(VNnames))])
        self.wait(1)
        for j in range(len(QNnames)) :
            msg[j].set_opacity(0)
        #Make QN and their edges fade
        QVNgroups.set_opacity(0)

        #Parity check values of CN
        txtCNbit = []
        CNbit = ["1","0","1","0"]
        for i in range(len(CNnames)) :
            #Add initial and final value
            txtCNbit.append([MathTex(CNbit[i],color=YELLOW).set_opacity(0).move_to(xCN*RIGHT + xycoord['yCN'+yCN][i]*UP), MathTex("0",color=YELLOW).set_opacity(0).move_to(xCN*RIGHT+xycoord['yCN'+yCN][i]*UP)])
        self.add_foreground_mobjects(*[txtCNbit[i][0] for i in range(len(CNbit))])
        self.add_foreground_mobjects(*[txtCNbit[i][1] for i in range(len(CNbit))])
        #Parity check values of VN
        txtVNbit = []
        VNbit = ["1","0","1","0"]
        VNpos = [3,4,5,1]
        for i in range(len(CNnames)) :
            #Add VN value
            txtVNbit.append(MathTex(VNbit[i],color=YELLOW).set_opacity(0).move_to(xVN*RIGHT + xycoord['yVN'+yVN][VNpos[i]]*UP))
        self.add_foreground_mobjects(*[txtVNbit[i][0] for i in range(len(VNbit))])
            
        #Create VN-CN groups for message passing
        for cnidx in range(len(CNnames)) :
            #Create all 3 (CN-VN-e) and edge only groups
            CNVNcxns = VGroup()
            edgeCNVNcxns = VGroup()
            revCNVNcxns = VGroup()
            #Add for highlight/indication
            CNonly = VGroup()
            VNonly = VGroup()

            #Add neighbouring VNs
            cnnd = CNnames[cnidx]
            #Add CNs
            CNVNcxns.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
            CNonly.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
            #Loop over neighbours
            for ng in tg[cnnd] :
                CNVNcxns.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                VNonly.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                #Obtained by printing the e in tg.edges format
                e = (cnnd,ng,0)
                #Reverse direction of above edge (VN to CN)
                erev = (ng,cnnd,0)
                #Add edge
                CNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                edgeCNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                #Add reverse edge from rev edge in same graph
                revCNVNcxns.add(mtg.edges[tg.edges[erev]['mob_id']])

            #Add groups into loop
            CNVNgroups.append(CNVNcxns)
            edgeCNVNgroups.append(edgeCNVNcxns)
            revCNVNgroups.append(revCNVNcxns)
            CNgroups.append(CNonly)
            VNgroups.append(VNonly)
        
        #Fade all
        self.add(*[CNVNgroups[i].set_opacity(0.15) for i in range(len(CNVNgroups))])
        #Order of CN message passing
        CNorder = [0,1,2,3]
        #Deduced VNs which need to be ON
        VNded = [None,None,0,1]
        for i in CNorder :
            CNVNgroups[i].set_opacity(1)
            if VNded[i] != None :
                txtVNbit[VNded[i]].set_opacity(1)
            #Pass the message from VN to CN
            msg = []
            for j in range(Z) :
                msg.append(Dot().set_color(PURPLE_B))
                #Change direction
            self.play(*[MoveAlongPath(msg[j],revCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
            #Parity-check bit VN to CN
            self.play(Indicate(CNgroups[i],color=PURPLE_B),
                      Transform(msg[0],txtCNbit[i][0].set_opacity(1)))
            for j in range(Z) :
                msg[j].set_opacity(0)

            #Pass from CN to VN
            msg = []
            for j in range(Z) :
                msg.append(Dot().set_color(GREEN))
            #Change direction
            self.play(*[MoveAlongPath(msg[j],edgeCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
            for j in range(Z) :
                msg[j].set_opacity(0)
            #Msg to be transformed
            msgtrans = [1,1,1,0]
            #Parity-check bit CN to VN
            self.play(Transform(txtCNbit[i][0],txtCNbit[i][1].set_opacity(1)),
                      Transform(msg[msgtrans[i]],txtVNbit[i].set_opacity(1)),
                      Indicate(VNgroups[i],color=GREEN),
                      scale_factor=1.1)
            self.wait(0.5)
            txtCNbit[i][0].set_opacity(0)
            self.play(FadeOut(txtCNbit[i][1]))
            txtVNbit[i].set_opacity(0.05)
            CNVNgroups[i].set_opacity(0.15)

        #Show Tx-Rx bits
        allNodes.set_opacity(0)
        self.add(*[CNVNgroups[i].set_opacity(0) for i in range(len(CNVNgroups))])
        allQNgroups.set_opacity(1)
        allVNgroups.set_opacity(1)
        for i in range(len(txtVNbit)) :
            txtVNbit[i].set_opacity(1)

        self.wait(2.5)
                


#################################################################################################################
'''
Animation 2 : Effect of Z on H
'''
#################################################################################################################
class BGtoH(Scene) :
    '''
    Using same BG show variation in H due to
    varying value of Z (3,5)
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z0 = 384
        Z1 = 2
        Z2 = 4
        shiftval0 = [106,-1,269,-1,-1,135,-1,212]
        shiftval1 = [0,-1,1,-1,-1,1,-1,0]
        shiftval2 = [2,-1,1,-1,-1,3,-1,0]
        BGmat0 = np.array([[106,-1,269,-1],[-1,135,-1,212]])
        BGmat1 = np.array([[0,-1,1,-1],[-1,1,-1,0]])
        BGmat2 = np.array([[2,-1,1,-1],[-1,3,-1,0]])
        #Create manim BG matrix
        manimBG0 = (Matrix((BGmat0.astype("int")).astype("str"),width=0.2,height=0.2)
               .scale(0.5)
               )
        manimBG1 = (Matrix((BGmat1.astype("int")).astype("str"),width=0.2,height=0.2)
               .scale(0.5)
               )
        manimBG2 = (Matrix((BGmat2.astype("int")).astype("str"),width=0.2,height=0.2)
               .scale(0.5)
               )
        manimBG0 = manimBG0.set_color(BLACK)
        manimBG1 = manimBG1.set_color(BLACK)
        manimBG2 = manimBG2.set_color(BLACK)

        #Text declarations of BG_Z
        txtBG0 = MathTex("{PM}_{Z=384} =",color=BLACK,height=0.4,width=1.5)
        txtBG1 = MathTex("{PM}_{Z=2} =",color=BLACK,height=0.4,width=1.3)
        txtBG2 = MathTex("{PM}_{Z=4} =",color=BLACK,height=0.4,width=1.3)

        txtmod1 = MathTex("{PM}_{Z=384}\pmod{2} \equiv",color=BLACK,height=0.4,width=2.5)
        txtmod2 = MathTex("{PM}_{Z=384}\pmod{4} \equiv",color=BLACK,height=0.4,width=2.5)

        txtH1 = MathTex("H_{Z=2} =",color=BLACK,height=0.4,width=1.3)
        txtH2 = MathTex("H_{Z=4} =",color=BLACK,height=0.4,width=1.3)
        
        #Text and BG_Z matrix animations
        txtBG0.move_to(-5*RIGHT)
        txtBG1.move_to(2.5*RIGHT + 2*UP)
        txtBG2.move_to(2.5*RIGHT + -2*UP)
        txtmod1.move_to(0.5*RIGHT + 2*UP)
        txtmod2.move_to(0.5*RIGHT + -2*UP)
        manimBG0.move_to(-2.5*RIGHT)
        manimBG1.move_to(5*RIGHT+ 2*UP)
        manimBG2.move_to(5*RIGHT+ -2*UP)

        self.play(FadeIn(txtBG0),run_time=1)
        self.play(FadeIn(manimBG0),run_time=1)
        self.play(FadeIn(txtmod1),
                  FadeIn(txtmod2),run_time=1)
        self.play(FadeIn(txtBG1),
                  FadeIn(txtBG2),run_time=1)
        self.play(FadeIn(manimBG1),
                  FadeIn(manimBG2),run_time=1)
        self.wait(1)

        #Fade others and slide the BG_Z1
        eqnBG1 = VGroup()
        eqnBG1.add(txtBG1)
        eqnBG1.add(manimBG1)
        eqnBG1.generate_target()
        eqnBG1.target.move_to(2*UP)
        
        self.play(FadeOut(txtBG0),
                  FadeOut(manimBG0),
                  FadeOut(txtmod1),
                  FadeOut(txtmod2),
                  FadeOut(txtBG2),
                  FadeOut(manimBG2))
        self.play(MoveToTarget(eqnBG1))

        #Create H animation
        #Create matrices from shift values
        shiftIM1 = []
        shiftIM2 = []
        for i in range(len(shiftval1)) :
            #For Z1
            mnm1 = genshiftedIM(shiftval1[i],N=Z1)
            mnm1 = mnm1.set_color(BLACK)
            brack1 = mnm1.get_brackets()
            brack1[0].set_color(WHITE)
            brack1[1].set_color(WHITE)
            shiftIM1.append(mnm1)

        #Positions of matrices
        x1,y1 = 1,-1
        #Z1
        x1off0 = 0.6
        x1off1 = 1.8
        shiftIM1[0].move_to((x1-x1off1)*RIGHT + (y1+1)*UP)
        shiftIM1[1].move_to((x1-x1off0)*RIGHT + (y1+1)*UP)
        shiftIM1[2].move_to((x1+x1off0)*RIGHT + (y1+1)*UP)
        shiftIM1[3].move_to((x1+x1off1)*RIGHT + (y1+1)*UP)
        #Row 2
        shiftIM1[4].move_to((x1-x1off1)*RIGHT + (y1)*UP)
        shiftIM1[5].move_to((x1-x1off0)*RIGHT + (y1)*UP)
        shiftIM1[6].move_to((x1+x1off0)*RIGHT + (y1)*UP)
        shiftIM1[7].move_to((x1+x1off1)*RIGHT + (y1)*UP)

        #Get manim indices of BG
        mnmidx = manimBG1.get_entries()
        #Create VGroups for H
        Hz1 = VGroup()
        #Obtain H from BG for Z1
        for i in range(len(shiftval1)) :
            #Obtain the index of BG
            self.play(
                Indicate(mnmidx[i],color=RED),
                TransformFromCopy(mnmidx[i],shiftIM1[i])
            )
            #Add to VGroup
            Hz1.add(shiftIM1[i])

        #Add H_z1 text and brackets
        txtH1.move_to(-3*RIGHT+ -0.5*UP)
        mnmbrack1 = add_brack(Hz1,Zval=2)
        Hbrack1 = VGroup()
        Hbrack1.add(txtH1)
        Hbrack1.add(mnmbrack1)
        self.play(FadeIn(Hbrack1))
        self.wait(1)
        #Fade all
        self.play(FadeOut(Hbrack1),
                  FadeOut(eqnBG1),
                  FadeOut(Hz1))
        
        ################ Similar animations for Z2 ##################
        #Fade in Z2 equation
        eqnBG2 = VGroup()
        eqnBG2.add(txtBG2)
        eqnBG2.add(manimBG2)
        eqnBG2.move_to(2*UP)
        self.play(FadeIn(eqnBG2))
        
        x2,y2 = 1,1.5
        shiftIM2 = []
        for i in range(len(shiftval2)) :
            #For Z2
            mnm2 = genshiftedIM(shiftval2[i],N=Z2)
            mnm2 = mnm2.set_color(BLACK)
            brack2 = mnm2.get_brackets()
            brack2[0].set_color(WHITE)
            brack2[1].set_color(WHITE)
            shiftIM2.append(mnm2)

        #Z2
        x2off0 = 1.25
        x2off1 = 3.75
        y2off0 = -1.5
        y2off1 = -3.2
        shiftIM2[0].move_to((x2-x2off1)*RIGHT + (y2+y2off0)*UP)
        shiftIM2[1].move_to((x2-x2off0)*RIGHT + (y2+y2off0)*UP)
        shiftIM2[2].move_to((x2+x2off0)*RIGHT + (y2+y2off0)*UP)
        shiftIM2[3].move_to((x2+x2off1)*RIGHT + (y2+y2off0)*UP)
        #Row 2
        shiftIM2[4].move_to((x2-x2off1)*RIGHT + (y2+y2off1)*UP)
        shiftIM2[5].move_to((x2-x2off0)*RIGHT + (y2+y2off1)*UP)
        shiftIM2[6].move_to((x2+x2off0)*RIGHT + (y2+y2off1)*UP)
        shiftIM2[7].move_to((x2+x2off1)*RIGHT + (y2+y2off1)*UP)
        
        #Get manim indices of BG
        mnmidx = manimBG2.get_entries()
        #Create VGroups for H
        Hz2 = VGroup()
        #Obtain H from BG for Z2
        for i in range(len(shiftval2)) :
            #Obtain the index of BG
            self.play(
                Indicate(mnmidx[i],color=RED),
                TransformFromCopy(mnmidx[i],shiftIM2[i])
            )
            #Add to VGroup
            Hz2.add(shiftIM2[i])
        
        #Add H_z2 text and brackets
        txtH2.move_to(-5.5*RIGHT+ -1*UP)
        mnmbrack2 = add_brack(Hz2,Zval=4)
        Hbrack2 = VGroup()
        Hbrack2.add(txtH2)
        Hbrack2.add(mnmbrack2)
        self.play(FadeIn(Hbrack2))
        self.wait(1)


#################################################################################################################
'''
Animation 3 : Obtain Tanner graph from H
'''
#################################################################################################################
class mattoTG(Scene) :
    '''
    Each highlighted row of a matrix is converted
    to a set of nodes and edges of the Tanner Graph
    '''
    def construct(self) :
        '''
        To construct the animation
        '''
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 3
        Nlayers = 2
        shiftval = [1,-1,2,-1,-1,0,-1,2]
        cshift = []
        shiftIM = []
        arrIM = []
        H = VGroup()
        #Create the shiftvalues and matrices
        for i in range(len(shiftval)) :
            cshift.append(Tex(str(shiftval[i]),color=BLACK))
            mnm,npa = genshiftedIM(shiftval[i],N=Z)
            mnm = mnm.set_color(BLACK)
            brack = mnm.get_brackets()
            brack[0].set_color(WHITE)
            brack[1].set_color(WHITE)
            shiftIM.append(mnm)
            H.add(shiftIM[i])
            arrIM.append(npa)

        #Define the shift/matrices position
        x,y = 2,3
        #Matrix positions
        xm,ym = 3,2
        #Row 1
        cshift[0].move_to(x*RIGHT + y*UP)
        cshift[1].move_to((x+1)*RIGHT + y*UP)
        cshift[2].move_to((x+2)*RIGHT + y*UP)
        cshift[3].move_to((x+3)*RIGHT + y*UP)
        #Row 2
        cshift[4].move_to(x*RIGHT + (y-1)*UP)
        cshift[5].move_to((x+1)*RIGHT + (y-1)*UP)
        cshift[6].move_to((x+2)*RIGHT + (y-1)*UP)
        cshift[7].move_to((x+3)*RIGHT + (y-1)*UP)
            
        #Tanner graph initialization
        CNnames = ['A','B','C','D','E','F']
        VNnames = ['0', '1', '2', '3', '4', '5','6','7','8','9','10','11']
        tg = tanner_graph(CNnames,len(VNnames),VNstoCN(array(arrIM[:4]))+","+VNstoCN(array(arrIM[4:])))
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
            
        #CN coordinates
        x1 = -6
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        x1 = -2
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node,tg_edge)

        #Begin animation
        #Create VGroups for PM
        PM = VGroup()
        #Entrance of shift values
        for i in range(len(shiftval)) :
            self.play(FadeIn(cshift[i]))
            PM.add(cshift[i])
        #Add PM text and brackets
        txtPM = MathTex("PM_{Z=3} =",color=BLACK)
        txtPM.move_to((x-2)*RIGHT+ (y-0.5)*UP)
        mnmbrack = add_brack(PM,Zval=2)
        PMbrack = VGroup()
        PMbrack.add(txtPM)
        PMbrack.add(mnmbrack)
        self.play(FadeIn(PMbrack))
        self.wait(1)

        #Fix matrix locations
        #Row 1
        shiftIM[0].move_to((xm-3)*RIGHT + (ym-2)*UP)
        shiftIM[1].move_to((xm-1)*RIGHT + (ym-2)*UP)
        shiftIM[2].move_to((xm+1)*RIGHT + (ym-2)*UP)
        shiftIM[3].move_to((xm+3)*RIGHT + (ym-2)*UP)
        #Row 2
        shiftIM[4].move_to((xm-3)*RIGHT + (ym-3.5)*UP)
        shiftIM[5].move_to((xm-1)*RIGHT + (ym-3.5)*UP)
        shiftIM[6].move_to((xm+1)*RIGHT + (ym-3.5)*UP)
        shiftIM[7].move_to((xm+3)*RIGHT + (ym-3.5)*UP)

        #Animate the matrices (highlight shift + transform)
        
        for i in range(len(shiftval)) :
            self.play(
                Indicate(cshift[i],color=RED),
                TransformFromCopy(cshift[i],shiftIM[i])
            )
        #Add box
        boxH = SurroundingRectangle(H,color=BLACK)
        self.play(FadeIn(boxH))
        #Labels around the matrices
        CNlabel = []
        VNlabel = []
        x2 = xm-4.35
        y2 = ym-1.6
        for i in range(len(CNnames)) :
            CNlabel.append(MathTex(r"C_{",CNnames[i],"}",height=0.2, color=BLACK))
            if i < len(CNnames)/Nlayers :
                CNlabel[i].move_to((x2*RIGHT + (y2-0.4*i)*UP))
            else :
                CNlabel[i].move_to((x2*RIGHT + (y2-0.3-0.4*i)*UP))

        x3 = xm-3.6
        y3 = ym-1
        for i in range(len(VNnames)) :
            VNlabel.append(MathTex("V_{",VNnames[i],"}",height=0.2, color=BLACK))
            VNlabel[i].move_to(((x3+0.65*i+0.05*(i//Z))*RIGHT + y3*UP))
        
        #Tanner graph animation
        self.play(*[FadeIn(mtg.nodes[tg.nodes[nd]['mob_id']])
                    for nd in CNnames],
                  *[FadeIn(CNlabel[i]) for i in range(len(CNnames))]
                  )
        self.play(*[FadeIn(mtg.nodes[tg.nodes[nd]['mob_id']])
                    for nd in VNnames],
                  *[FadeIn(VNlabel[i]) for i in range(len(VNnames))]
                  )

        self.add_foreground_mobjects(*mtg.nodes.values())
        self.wait(1)
        #Add CN-VN labels along matrix?
        '''
        If h/w implemented, then use mod to get
        non-zero values
        '''
        #Loop across number of shiftvalues
        nz = []
        for i in range(len(shiftval)) :
            #Get non-zero indices in each expansion
            nz.append(np.where(arrIM[i]!=0))
            
        #Loop across rows/CNs
        redidx = np.zeros(len(shiftval))
        #Fading group
        edgefade = VGroup()
        for k in range(Nlayers) :
            for i in range(Z) :
                #Take nz values of each row across shifts
                rowvg = VGroup()
                onesvg = VGroup()
                for j in range(int(len(shiftval)/Nlayers)) :
                    #Shift-index based on layer value
                    jlayer = int(k*int(len(shiftval)/Nlayers))+ j
                    #Skip zero blocks
                    if len(nz[jlayer][1]) == 0 :
                        continue
                    #Make nz of each expansion red
                    colnz = nz[jlayer][1][i]  #Choose nz column of ith row/CN
                    #This is done since manimmatrix.get_entries() has
                    #linear/flat indices which go from 0-9 for a 3x3
                    #matrix like in matlab
                    nzred = np.ravel_multi_index([[i],[colnz]],(Z,Z))  #Obtain flat index value
                    #This is done since the VNlabels are flat
                    #from 0 to len(shiftval)
                    labelred = np.ravel_multi_index([[j],[colnz]],(int(len(shiftval)/Nlayers),Z))  #Obtain flat label index

                    mnmidx = shiftIM[jlayer].get_entries()
                    #Create row group
                    rowvg.add(shiftIM[jlayer].get_rows()[i])

                    #Make nz ith row indices highlight
                    onesvg.add(mnmidx[nzred[0]])
                    onesvg.add(VNlabel[labelred[0]])
                    onesvg.add(CNlabel[int(k*Z)+i])

                self.play(Indicate(onesvg,color=RED))
                self.wait(1)
                #Fade the older edges
                edgefade.set_opacity(0.15)
                #Make edges red initially
                self.play(*[TransformFromCopy(rowvg,mtg.edges[tg.edges[e]['mob_id']])
                        for e in tg.edges(CNnames[int(k*Z)+i],keys=True)])
                #Add older edges to fade
                for e in tg.edges(CNnames[k*Z+i],keys=True) :
                    edgefade.add(mtg.edges[tg.edges[e]['mob_id']])
                
        self.wait(1)
        #Unfade all edges
        edgefade.set_opacity(1)

#################################################################################################################
'''
Animation 4 : Layered v/s Flooding
'''
#################################################################################################################
class FloodvsLayer(Scene) :
    '''
    Move circle through/over edge from VN to CN
    and square through edge from CN to VN
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 3
        shiftval = [1,-1,2,-1,-1,0,-1,2]
        #Total edges = NZ*Z (since each NZ entry upon
        #expansion has Z non-zero entries => Z edges)
        Nedges = Z*len(np.where(np.array(shiftval)!=-1)[0])
        Niter = 1
        arrIM = []
        #Create the shiftvalues and matrices
        for i in range(len(shiftval)) :
            _,npa = genshiftedIM(shiftval[i],N=Z)
            arrIM.append(npa)

        #Tanner graph initialization
        CNnames = ['A','B','C','D','E','F']
        VNnames = ['0', '1', '2', '3', '4', '5','6','7','8','9','10','11']
        tg = tanner_graph(CNnames,len(VNnames),VNstoCN(array(arrIM[:4]))+","+VNstoCN(array(arrIM[4:])))
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
            
        #CN coordinates
        x1 = -3
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        x1 = 2
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node,tg_edge)
        
        #Add to make edges go behind variables
        self.add_foreground_mobjects(*mtg.nodes.values())

        #Begin fade animation
        CNVNgroups = []

        ########################################### FLOODING ###################################################

        #Text heading
        txtFlood = Text("Flooding schedule",color=BLACK).scale(0.5)
        self.play(FadeIn(txtFlood.move_to(4*LEFT+3.5*UP)),run_time=1)
        #Add for highlight/indication
        CNonly = VGroup()
        VNonly = VGroup()
        #Add edge and their reverse in groups
        edgeCNVNcxns = VGroup()
        revCNVNcxns = VGroup()
        #Add all VNs
        for vnnd in VNnames :
            VNonly.add(mtg.nodes[tg.nodes[vnnd]['mob_id']])
        #Add all CNs
        for cnnd in CNnames :
            CNonly.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
            #Add edges and revedge
            for ng in tg[cnnd] :
                e = (cnnd,ng,0)
                erev = (ng,cnnd,0)
                edgeCNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                revCNVNcxns.add(mtg.edges[tg.edges[erev]['mob_id']])

        #Make edges visible
        self.add(edgeCNVNcxns.set_opacity(1))

        #Perform MP
        for iters in range(Niter) :
            #Send messages from VN to CN
            msg = []
            for j in range(Nedges) :
                msg.append(Dot().set_color(PURPLE_B))
            self.play(*[MoveAlongPath(msg[j],revCNVNcxns[j]) for j in range(Nedges)],rate_func=slow_into)
            for j in range(Nedges) :
                msg[j].set_opacity(0)
            self.play(Indicate(CNonly,color=PURPLE_B),scale_factor=1.1)
            #Send messages from CN to VN
            msg = []
            for j in range(Nedges) :
                msg.append(Dot().set_color(GREEN))
            self.play(*[MoveAlongPath(msg[j],edgeCNVNcxns[j]) for j in range(Nedges)],rate_func=slow_into)
            for j in range(Nedges) :
                msg[j].set_opacity(0)
            self.play(Indicate(VNonly,color=GREEN),scale_factor=1.05)
            
        self.play(FadeOut(txtFlood))
        self.wait(1)            
        
        ########################################### LAYERED #####################################################

        #Text heading
        txtLayer = Text("Layered schedule",color=BLACK).scale(0.5)
        self.play(FadeIn(txtLayer.move_to(4*LEFT+3.5*UP)),run_time=1)
        #Obtain group for animation along edge and reverse
        edgeCNVNgroups = []
        revCNVNgroups = []
        CNgroups = []
        VNgroups = []
        
        for cn in range(len(CNnames)) :
            #Add for highlight/indication
            CNonly = VGroup()
            VNonly = VGroup()
            #Add edge and their reverse in groups
            edgeCNVNcxns = VGroup()
            revCNVNcxns = VGroup()
            
            #Do MP
            cnnd = CNnames[cn]
            CNonly.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
            #Use neighbors to add connected VNs/edges
            for ng in tg[cnnd] :
                VNonly.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                e = (cnnd,ng,0)
                erev = (ng,cnnd,0)
                edgeCNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                revCNVNcxns.add(mtg.edges[tg.edges[erev]['mob_id']])

            #Add groups into list
            CNgroups.append(CNonly)
            VNgroups.append(VNonly)
            edgeCNVNgroups.append(edgeCNVNcxns)
            revCNVNgroups.append(revCNVNcxns)

        #Make edges visible
        self.add(*[CNgroups[i].set_opacity(0.15) for i in range(len(CNgroups))],
                 *[VNgroups[i].set_opacity(0.15) for i in range(len(VNgroups))],
                 *[edgeCNVNgroups[i].set_opacity(0.15) for i in range(len(edgeCNVNgroups))])
        #Perform MP
        for iters in range(Niter) :
            for cn in range(len(CNnames)) :
                #Send messages from VN to CN
                #Darken
                CNgroups[cn].set_opacity(1)
                VNgroups[cn].set_opacity(1)
                edgeCNVNgroups[cn].set_opacity(1)
                msg = []
                for j in range(len(revCNVNgroups[cn])) :
                    msg.append(Dot().set_color(PURPLE_B))
                self.play(*[MoveAlongPath(msg[j],revCNVNgroups[cn][j]) for j in range(len(revCNVNgroups[cn]))],rate_func=slow_into)
                #Fade the message ball
                for j in range(len(revCNVNgroups[cn])) :
                    msg[j].set_opacity(0)
                self.play(Indicate(CNgroups[cn],color=PURPLE_B))
                
                #Send messages from CN to VN
                msg = []
                for j in range(len(revCNVNgroups[cn])) :
                    msg.append(Dot().set_color(GREEN))
                self.play(*[MoveAlongPath(msg[j],edgeCNVNgroups[cn][j]) for j in range(len(revCNVNgroups[cn]))],rate_func=slow_into)
                #Fade the message ball
                for j in range(len(revCNVNgroups[cn])) :
                    msg[j].set_opacity(0)
                self.play(Indicate(VNgroups[cn],color=GREEN),scale_factor=1.1)
                #Lighten
                CNgroups[cn].set_opacity(0.15)
                VNgroups[cn].set_opacity(0.15)
                edgeCNVNgroups[cn].set_opacity(0.15)

                
#################################################################################################################
'''
Animation 5 : Algorithm flow with time
'''
#################################################################################################################
class BGandTG(Scene) :
    '''
    Simultaneously show side-by-side functioning
    of base graph and tanner graph
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 3
        shiftval = [1,0,1,1,0,-1,0,0]
        arrIM = []
        #Create the shiftvalues and matrices
        for i in range(len(shiftval)) :
            _,npa = genshiftedIM(shiftval[i],N=Z)
            arrIM.append(npa)

        #Tanner graph initialization
        CNnames = ['A','B','C','D','E','F']
        VNnames = ['0', '1', '2', '3', '4', '5','6','7','8','9','10','11']
        tg = tanner_graph(CNnames,len(VNnames),VNstoCN(array(arrIM[:4]))+","+VNstoCN(array(arrIM[4:])))
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
            
        #CN coordinates
        x1 = -3
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        x1 = 2
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node,tg_edge)
        #Add to make edges go behind variables
        self.add_foreground_mobjects(*mtg.nodes.values())

        #Begin fade animation
        CNVNgroups = []
        
        for BGrows in range(int(len(CNnames)/Z)) :
            #Need to include Z CNs in all BG columns
            for BGcol in range(int(len(VNnames)/Z)) :
                #Remove group if shiftval is -1
                if shiftval[int(BGrows*(len(VNnames)/Z))+BGcol] == -1 :
                    continue
                CNVNcxns = VGroup()
                #Add all Z CNs in group
                for nd in range(Z) :
                    #Obtain CN id
                    cnnd = CNnames[int(Z*BGrows)+nd]
                    #Add Z CNs
                    CNVNcxns.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
                    #Loop over neighbours
                    for ng in tg.neighbors(cnnd) :
                        #Add if neighbour is in the BGcol
                        lowbound = BGcol*Z
                        upbound = (BGcol+1)*Z
                        ngint = int(ng)
                        if ngint >= lowbound and ngint < upbound :
                            #Add VN to group
                            CNVNcxns.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                            #Obtained by printing the e in tg.edges format
                            e = (cnnd,ng,0)
                            #Add edge
                            CNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                            break
                #Add groups into loop
                CNVNgroups.append(CNVNcxns)
                
        #Fade all
        self.add(*[CNVNgroups[i].set_opacity(0.15) for i in range(len(CNVNgroups))])
        #Fade others
        for i in range(len(CNVNgroups)) :
            CNVNgroups[i].set_opacity(1)
            self.wait(2)
            CNVNgroups[i].set_opacity(0.15)


#################################################################################################################
'''
Animation 6 : Outlook on decoding
'''
#################################################################################################################
class QandTG(Scene) :
    '''
    Move circle through/over edge from VN to CN
    and square through edge from CN to VN
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 3
        #shiftval = [0,2,-1,1,1,2,2,1]
        shiftval = [1,-1,2,-1,-1,0,-1,2]
        arrIM = []
        #Create the shiftvalues and matrices
        for i in range(len(shiftval)) :
            _,npa = genshiftedIM(shiftval[i],N=Z)
            arrIM.append(npa)

        #Tanner graph initialization
        CNnames = ['A','B','C','D','E','F']
        #CNnames = ['12','13','14','15','16','17']
        VNnames = ['0', '1', '2', '3', '4', '5','6','7','8','9','10','11']
        #QNnames = []
        QNnames = ['G','H','I','J','K','L','M','N','O','P','Q','R']
        tg = tanner_graph_OUTLOOK(CNnames,len(VNnames),VNstoCN(array(arrIM[:4])) + ","+VNstoCN(array(arrIM[4:])),QNnames)
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
            
        #CN coordinates
        x1 = -4
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        x1 = 1
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)
        
        #QN coordinates
        x2 = 3
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x2
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',QNnames , pos, tg)
        

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node_OUTLOOK,tg_edge)
        
        #Add to make edges go behind variables
        self.add_foreground_mobjects(*mtg.nodes.values())

        #Begin fade animation
        CNVNgroups = []
        #Obtain group for animation along edge and reverse
        edgeCNVNgroups = []
        revCNVNgroups = []
        CNgroups = []
        VNgroups = []
        NZcumsum = [0]

        #Create all node groups for box
        allQNgroups = VGroup()
        allVNgroups = VGroup()
        allCNgroups = VGroup()
        #Create groups to handle together
        for i in range(len(QNnames)) :
            allQNgroups.add(mtg.nodes[tg.nodes[QNnames[i]]['mob_id']])
            allVNgroups.add(mtg.nodes[tg.nodes[VNnames[i]]['mob_id']])
        for i in range(len(CNnames)) :
            allCNgroups.add(mtg.nodes[tg.nodes[CNnames[i]]['mob_id']])

        #Add a box around CN-VN
        boxCNVN = VGroup()
        boxCNVN.add(allVNgroups)
        boxCNVN.add(allCNgroups)
        rectCNVN = SurroundingRectangle(boxCNVN,fill_color=YELLOW,fill_opacity=0.7, buff=MED_LARGE_BUFF)
        self.add(rectCNVN)
        txtEstLLR = Text(" Improve\n estimated LLR",color=BLACK).scale(0.6)
        txtEstLLR.move_to(-1.5*RIGHT)
        txtEstLLR.set_opacity(0)

        #Add Q-VN edges
        QVNgroups = VGroup()
        for qnd in QNnames :
            for ng in tg.neighbors(qnd) :
                if tg.nodes[ng]['type'] == 'variablenode' :
                    e = (qnd,ng,0)
                    QVNgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(QVNgroups.set_opacity(1))
        #Make all QNs, VNs visible
        allQNgroups.set_opacity(1)
        allVNgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(RED_D))
        #Send message
        self.play(*[MoveAlongPath(msg[j],QVNgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        self.play(Indicate(allVNgroups,color=RED_D,scale_factor=1.05))
        for j in range(len(QNnames)) :
            msg[j].set_opacity(0)
        #Make QN and their edges fade
        allQNgroups.set_opacity(0.15)
        QVNgroups.set_opacity(0.15)
            
        
        for BGrows in range(int(len(CNnames)/Z)) :
            #Need to include Z CNs in all BG columns
            NZvar = 0
            for BGcol in range(int(len(VNnames)/Z)) :
                #Remove group if shiftval is -1
                if shiftval[int(BGrows*(len(VNnames)/Z))+BGcol] == -1 :
                    continue
                #Increment NZ val
                NZvar += 1
                CNVNcxns = VGroup()
                #Add edge and their reverse in groups
                edgeCNVNcxns = VGroup()
                revCNVNcxns = VGroup()
                #Add for highlight/indication
                CNonly = VGroup()
                VNonly = VGroup()
                
                #Add all Z CNs in group
                for nd in range(Z) :
                    #Obtain CN id
                    cnnd = CNnames[int(Z*BGrows)+nd]
                    #Add Z CNs (for the highlight too)
                    CNVNcxns.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
                    CNonly.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
                    
                    #Loop over neighbours
                    for ng in tg[cnnd] :
                        #Add if neighbour is in the BGcol
                        lowbound = BGcol*Z
                        upbound = (BGcol+1)*Z
                        ngint = int(ng)
                        
                        if ngint >= lowbound and ngint < upbound :
                            #Add VN to group (for the highlight too)
                            CNVNcxns.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                            VNonly.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                            #Obtained by printing the e in tg.edges format
                            e = (cnnd,ng,0)
                            #Reverse direction of above edge (VN to CN)
                            erev = (ng,cnnd,0)
                            #Add edge
                            CNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                            edgeCNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                            #Add reverse edge from rev edge in same graph
                            revCNVNcxns.add(mtg.edges[tg.edges[erev]['mob_id']])
                            #print(mtg.edges[tg.edges[e]['mob_id']])
                            break
                        
                #Add groups into loop
                CNVNgroups.append(CNVNcxns)
                edgeCNVNgroups.append(edgeCNVNcxns)
                revCNVNgroups.append(revCNVNcxns)
                CNgroups.append(CNonly)
                VNgroups.append(VNonly)

            #Add NZ cum sum
            NZcumsum.append(NZvar+NZcumsum[-1])

        #Add VN-Q edges
        VNQgroups = VGroup()
        for qnd in QNnames :
            for ng in tg.neighbors(qnd) :
                if tg.nodes[ng]['type'] == 'variablenode' :
                    e = (ng,qnd,0)
                    VNQgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(VNQgroups.set_opacity(0.15))
        
        #Fade all
        self.add(*[CNVNgroups[i].set_opacity(0.15) for i in range(len(CNVNgroups))])
        #Fade others
        for n in range(len(NZcumsum)-1) :
            #Loop over NZ VGgroup of each layer (VN to CN)
            for i in range(NZcumsum[n],NZcumsum[n+1]) :
                CNVNgroups[i].set_opacity(1)
                #Pass the message from VN to CN
                msg = []
                for j in range(Z) :
                    msg.append(Dot().set_color(PURPLE_B))
                #Change direction
                self.play(*[MoveAlongPath(msg[j],revCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
                for j in range(Z) :
                    msg[j].set_opacity(0)
                self.play(Indicate(CNgroups[i],color=PURPLE_B))
                #self.wait(2)
                CNVNgroups[i].set_opacity(0.15)

            #Loop over NZ VGgroup of each layer (VN to CN)
            for i in range(NZcumsum[n],NZcumsum[n+1]) :
                CNVNgroups[i].set_opacity(1)
                #Pass from CN to VN
                msg = []
                for j in range(Z) :
                    msg.append(Dot().set_color(GREEN))
                #Change direction
                self.play(*[MoveAlongPath(msg[j],edgeCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
                for j in range(Z) :
                    msg[j].set_opacity(0)
                self.play(Indicate(VNgroups[i],color=GREEN))
                #self.wait(2)
                CNVNgroups[i].set_opacity(0.15)

            
        #Make all QNs,VNs and their edges visible
        allQNgroups.set_opacity(1)
        allVNgroups.set_opacity(1)
        VNQgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(PURPLE_B))        
        #Receive message
        self.play(*[MoveAlongPath(msg[j],VNQgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        self.play(Indicate(allQNgroups,color=PURPLE_B,scale_factor=1.05))

        #Fade all
        self.add(*[CNVNgroups[i].set_opacity(0) for i in range(len(CNVNgroups))],
                 *allVNgroups.set_opacity(0),
                 *allCNgroups.set_opacity(0),
                 rectCNVN.set_opacity(1),
                 txtEstLLR.set_opacity(1))

        for iters in range(2) :
            #Receive message
            #Pass the message from VN to Q            
            msg = []
            for j in range(len(QNnames)) :
                msg.append(Dot().set_color(RED_D))
            self.play(*[MoveAlongPath(msg[j],QVNgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
            for j in range(len(QNnames)) :
                msg[j].set_opacity(0)
            self.wait(2)
            #Send message
            #Pass the message from VN to Q            
            msg = []
            for j in range(len(QNnames)) :
                msg.append(Dot().set_color(PURPLE_B))
            self.play(*[MoveAlongPath(msg[j],VNQgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
            self.play(Indicate(allQNgroups,color=PURPLE_B,scale_factor=1.05))
            for j in range(len(QNnames)) :
                msg[j].set_opacity(0)
            self.wait(1)


#################################################################################################################
'''
Animation 7 : All steps of OMS QC-LDPC decoding
'''
#################################################################################################################
class OMS(Scene) :
    '''
    Move circle through/over edge from VN to CN
    and square through edge from CN to VN
    '''
    def construct(self) :
        #Set background color
        self.camera.background_color = WHITE
        #Constants and variables
        Z = 3
        shiftval = [1,-1,2,-1,-1,0,-1,2]
        arrIM = []
        #Create the shiftvalues and matrices
        for i in range(len(shiftval)) :
            _,npa = genshiftedIM(shiftval[i],N=Z)
            arrIM.append(npa)

        #Tanner graph initialization
        CNnames = ['A','B','C','D','E','F']
        #CNnames = ['12','13','14','15','16','17']
        VNnames = ['0', '1', '2', '3', '4', '5','6','7','8','9','10','11']
        #QNnames = []
        QNnames = ['G','H','I','J','K','L','M','N','O','P','Q','R']
        INnames = ['g','h','i','j','k','l','m','n','o','p','q','r']
        tg = tanner_graph_OMS(CNnames,len(VNnames),VNstoCN(array(arrIM[:4])) + ","+VNstoCN(array(arrIM[4:])),QNnames,INnames)
        
        xycoord = {'yCN3' : np.arange(2,-3,-2),
                   'yVN9' : np.arange(8/3,-3,-2/3),
                   'yCN6' : np.arange(2.5,-3,-1),
                   'yVN12' : np.arange(3.3,-3.4,-3/5)
                   }
        #Give coordinates based on CN-VN length
        if len(CNnames) == 6 and len(VNnames) == 12 :
            yCN = '6'
            yVN = '12'
        elif len(CNnames) == 3 and len(VNnames) == 9 :
            yCN = '3'
            yVN = '9'
            
        #CN coordinates
        x1 = -4
        pos = np.zeros((len(CNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yCN'+yCN]
        mnx.map_attr('pos', CNnames, pos, tg)
        #VN coordinates
        x1 = 1
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x1
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',VNnames , pos, tg)
        #QN coordinates
        x2 = 3
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x2
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',QNnames , pos, tg)
        #IN coordinates
        x2 = 5
        pos = np.zeros((len(VNnames), 2))
        pos[:, 0] = x2
        pos[:, 1] = xycoord['yVN'+yVN]
        mnx.map_attr('pos',INnames , pos, tg)
        

        #define the manim graph
        mtg = mnx.ManimGraph(tg,tg_node_OMS,tg_edge)
        
        #Add to make edges go behind variables
        self.add_foreground_mobjects(*mtg.nodes.values())

        #Begin fade animation
        CNVNgroups = []
        #Obtain group for animation along edge and reverse
        edgeCNVNgroups = []
        revCNVNgroups = []
        CNgroups = []
        VNgroups = []
        NZcumsum = [0]

        #Create all node groups for box
        allQNgroups = VGroup()
        allVNgroups = VGroup()
        allCNgroups = VGroup()
        allINgroups = VGroup()
        #Create groups to handle together
        for i in range(len(QNnames)) :
            allQNgroups.add(mtg.nodes[tg.nodes[QNnames[i]]['mob_id']])
            allVNgroups.add(mtg.nodes[tg.nodes[VNnames[i]]['mob_id']])
            allINgroups.add(mtg.nodes[tg.nodes[INnames[i]]['mob_id']])
        for i in range(len(CNnames)) :
            allCNgroups.add(mtg.nodes[tg.nodes[CNnames[i]]['mob_id']])

        #Add a box around CN-VN
        txtInt = Text("Interface",color=YELLOW).scale(0.4)
        boxINVN = VGroup()
        boxINVN.add(allINgroups)
        rectINVN = SurroundingRectangle(boxINVN,color=DARK_BROWN,fill_color=DARK_BROWN,fill_opacity=1, buff=MED_LARGE_BUFF)
        self.add(rectINVN)
        self.add(txtInt.shift(5*RIGHT))
        #Add to make nodes go behind text
        self.add_foreground_mobjects(txtInt)
        #Add a box around CN-VN
        boxCNVN = VGroup()
        boxCNVN.add(allVNgroups)
        boxCNVN.add(allCNgroups)
        rectCNVN = SurroundingRectangle(boxCNVN,fill_color=YELLOW,fill_opacity=0.7, buff=MED_LARGE_BUFF)
        self.add(rectCNVN)
        
        #Mode input
        txtIp = Text("Input mode",color=BLACK).scale(0.5)
        self.play(FadeIn(txtIp.move_to(6*LEFT+3.5*UP)),run_time=0.1)
        #Add QN-IN edges
        INQNgroups = VGroup()
        for ind in INnames :
            for ng in tg.neighbors(ind) :
                if tg.nodes[ng]['type'] == 'qnode' :
                    e = (ind,ng,0)
                    INQNgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(INQNgroups.set_opacity(1))
        
        #Make all QNs,INs and their edges visible
        allQNgroups.set_opacity(1)
        #allINgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(DARK_BROWN))        
        #Receive message
        self.play(*[MoveAlongPath(msg[j],INQNgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        self.play(Indicate(allQNgroups,color=DARK_BROWN,scale_factor=1.05))
        for j in range(len(QNnames)) :
            msg[j].set_opacity(0)
        #Make QN and their edges fade
        INQNgroups.set_opacity(0)
        #Mode iteration
        self.play(FadeOut(txtIp),run_time=0.1)
        txtIter = Text("Iteration",color=BLACK).scale(0.5)
        txtMode = Text("mode",color=BLACK).scale(0.5)
        txtLLRr = Text("LLR Read",color=BLACK).scale(0.5)
        self.play(FadeIn(txtIter.move_to(6*LEFT+3.5*UP)),
                  FadeIn(txtMode.move_to(6*LEFT+3.2*UP)),
                  FadeIn(txtLLRr.move_to(6*LEFT+2.7*UP)),run_time=0.1)
        
        #Add Q-VN edges
        QVNgroups = VGroup()
        for qnd in QNnames :
            for ng in tg.neighbors(qnd) :
                if tg.nodes[ng]['type'] == 'variablenode' :
                    e = (qnd,ng,0)
                    QVNgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(QVNgroups.set_opacity(1))
        #Make all QNs, VNs visible
        allQNgroups.set_opacity(1)
        allVNgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(RED_D))
        #Send message
        self.play(*[MoveAlongPath(msg[j],QVNgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        self.play(Indicate(allVNgroups,color=RED_D,scale_factor=1.05))
        for j in range(len(QNnames)) :
            msg[j].set_opacity(0)
        #Make QN's edges fade
        QVNgroups.set_opacity(0)            
        
        for BGrows in range(int(len(CNnames)/Z)) :
            #Need to include Z CNs in all BG columns
            NZvar = 0
            for BGcol in range(int(len(VNnames)/Z)) :
                #Remove group if shiftval is -1
                if shiftval[int(BGrows*(len(VNnames)/Z))+BGcol] == -1 :
                    continue
                #Increment NZ val
                NZvar += 1
                CNVNcxns = VGroup()
                #Add edge and their reverse in groups
                edgeCNVNcxns = VGroup()
                revCNVNcxns = VGroup()
                #Add for highlight/indication
                CNonly = VGroup()
                VNonly = VGroup()
                
                #Add all Z CNs in group
                for nd in range(Z) :
                    #Obtain CN id
                    cnnd = CNnames[int(Z*BGrows)+nd]
                    #Add Z CNs (for the highlight too)
                    CNVNcxns.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
                    CNonly.add(mtg.nodes[tg.nodes[cnnd]['mob_id']])
                    
                    #Loop over neighbours
                    for ng in tg[cnnd] :
                        #Add if neighbour is in the BGcol
                        lowbound = BGcol*Z
                        upbound = (BGcol+1)*Z
                        ngint = int(ng)
                        
                        if ngint >= lowbound and ngint < upbound :
                            #Add VN to group (for the highlight too)
                            CNVNcxns.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                            VNonly.add(mtg.nodes[tg.nodes[ng]['mob_id']])
                            #Obtained by printing the e in tg.edges format
                            e = (cnnd,ng,0)
                            #Reverse direction of above edge (VN to CN)
                            erev = (ng,cnnd,0)
                            #Add edge
                            CNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                            edgeCNVNcxns.add(mtg.edges[tg.edges[e]['mob_id']])
                            #Add reverse edge from rev edge in same graph
                            revCNVNcxns.add(mtg.edges[tg.edges[erev]['mob_id']])
                            break
                        
                #Add groups into list
                CNVNgroups.append(CNVNcxns)
                edgeCNVNgroups.append(edgeCNVNcxns)
                revCNVNgroups.append(revCNVNcxns)
                CNgroups.append(CNonly)
                VNgroups.append(VNonly)

            #Add NZ cum sum
            NZcumsum.append(NZvar+NZcumsum[-1])

        #Add VN-Q edges
        VNQgroups = VGroup()
        for qnd in QNnames :
            for ng in tg.neighbors(qnd) :
                if tg.nodes[ng]['type'] == 'variablenode' :
                    e = (ng,qnd,0)
                    VNQgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(VNQgroups.set_opacity(0))

        #Add QN-IN edges
        QNINgroups = VGroup()
        for ind in INnames :
            for ng in tg.neighbors(ind) :
                if tg.nodes[ng]['type'] == 'qnode' :
                    e = (ng,ind,0)
                    QNINgroups.add(mtg.edges[tg.edges[e]['mob_id']])
            
        self.add(QNINgroups.set_opacity(0))
        
        #Fade all
        self.play(FadeOut(txtLLRr.move_to(6*LEFT+2.7*UP)),run_time=0.1)
        self.add(*[CNVNgroups[i].set_opacity(0.15) for i in range(len(CNVNgroups))],
                 *[edgeCNVNgroups[i].set_opacity(0) for i in range(len(CNVNgroups))])
        #Fade others
        txtCN = Text("CN update",color=BLACK).scale(0.5)
        txtVN = Text("VN update",color=BLACK).scale(0.5)
        txtLLRw = Text("LLR Write",color=BLACK).scale(0.5)
        for n in range(len(NZcumsum)-1) :
            #Loop over NZ VGgroup of each layer (VN to CN)
            #Mode CN update
            self.play(FadeIn(txtCN.move_to(6*LEFT+2.7*UP)),run_time=0.1)
            for i in range(NZcumsum[n],NZcumsum[n+1]) :
                CNVNgroups[i].set_opacity(1)
                #Pass the message from VN to CN
                msg = []
                for j in range(Z) :
                    msg.append(Dot().set_color(PURPLE_B))
                #Change direction
                self.play(*[MoveAlongPath(msg[j],revCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
                for j in range(Z) :
                    msg[j].set_opacity(0)
                self.play(Indicate(CNgroups[i],color=PURPLE_B))
                CNVNgroups[i].set_opacity(0.15)
                edgeCNVNgroups[i].set_opacity(0)
                #Change mode
            self.play(FadeOut(txtCN),run_time=0.1)

            #Loop over NZ VGgroup of each layer (VN to CN)
            #Mode VN update
            self.play(FadeIn(txtVN.move_to(6*LEFT+2.7*UP)),run_time=0.1)
            for i in range(NZcumsum[n],NZcumsum[n+1]) :
                CNVNgroups[i].set_opacity(1)
                #Pass from CN to VN
                msg = []
                for j in range(Z) :
                    msg.append(Dot().set_color(GREEN))
                #Change direction
                self.play(*[MoveAlongPath(msg[j],edgeCNVNgroups[i][j]) for j in range(Z)],rate_func=slow_into)
                for j in range(Z) :
                    msg[j].set_opacity(0)
                self.play(Indicate(VNgroups[i],color=GREEN))
                CNVNgroups[i].set_opacity(0.15)
                edgeCNVNgroups[i].set_opacity(0)
                #Change mode
            self.play(FadeOut(txtVN),run_time=0.1)

            
        #Make all QNs,VNs and their edges visible
        #Mode CN update
        self.play(FadeIn(txtLLRw.move_to(6*LEFT+2.7*UP)),run_time=0.1)
        allQNgroups.set_opacity(1)
        allVNgroups.set_opacity(1)
        allCNgroups.set_opacity(1)
        VNQgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(PURPLE_B))        
        #Receive message
        self.play(*[MoveAlongPath(msg[j],VNQgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        self.play(Indicate(allQNgroups,color=PURPLE_B,scale_factor=1.05))
        

        #Mode i/o
        txtOp = Text("Output mode",color=BLACK).scale(0.5)
        self.play(FadeOut(txtIter),
                  FadeOut(txtMode),
                  FadeOut(txtLLRw),
                  FadeIn(txtOp.move_to(6*LEFT+3.5*UP)),run_time=0.1)
        #Make all QNs,INs and their edges visible
        VNQgroups.set_opacity(0)
        #allINgroups.set_opacity(1)
        QNINgroups.set_opacity(1)
        #Pass the message from VN to Q            
        msg = []
        for j in range(len(QNnames)) :
            msg.append(Dot().set_color(YELLOW))        
        #Receive message
        self.play(*[MoveAlongPath(msg[j],QNINgroups[j]) for j in range(len(QNnames))],rate_func=slow_into)
        
