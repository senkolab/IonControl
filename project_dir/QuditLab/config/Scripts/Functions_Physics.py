#Functions_Physics.py created 2022-06-30 15:54:40.267595
import sys
import numpy as np
import math
sys.path.append(r'C:\Users\ions\Documents\IonControl\scripting')
from Script import *

from sympy.physics.wigner import wigner_3j
from sympy.physics.wigner import wigner_6j

amu_Conv = 1.660539040e-27
c = 2.99792458e8
muB = 1.399624624
hbar = 1.0545718e-34
h = 2*math.pi*hbar

#Nearly immutable constants
S = 1/2
gS = 2.002319
gL = 1

#Class BariumTransition: defines a optical transition in barium. Input Isotope (string), AtomicNumbersFine (list [I, J, Jp]), Freq_Offset=0 (from Ba138), Freq=541.43300e12, HyperFine = [0, 0], ZeemanNumbers = [0, 0], Abundance = 1, GraphVertOff = 0
#method S_FF: calculates the transition number S_ff, method TransitionStrength: calculates the overall transition strength of a specific mf-mf' transition, method AverageFTransitionStrength: calculates the average transition strength of all mf-mf' transitions of F-F'
#method AverageTransitionStrength: calculates the average transition strength of all transitions, method TransitionFreq: gives the overall transition frequency, method ChangeHyperFine: allows you to change the HF structure values, method Add_gvert
class BariumTransition:
    def __init__(self, Isotope, AtomicNumbersFine, Freq_Offset=0, Freq=541.43300e12, HyperFine = [0, 0], ZeemanNumbers = [0, 0], Abundance = 1, GraphVertOff = 0):
        self.m = Isotope
        self.I = AtomicNumbersFine[0]
        self.J = AtomicNumbersFine[1]
        self.Jp = AtomicNumbersFine[2]
        self.F = HyperFine[0]
        self.Fp = HyperFine[1]
        self.m_F = ZeemanNumbers[0]
        self.m_Fp = ZeemanNumbers[1]                    
        self.freq = Freq
        self.freq_Off = Freq_Offset
        self.abund = Abundance
        self.gvert = GraphVertOff
        
    def S_FF(self, m_F):
        Coeff = math.sqrt((2*self.Fp + 1)*(2*self.F + 1)*(2*self.J+1))
        SixJ = wigner_6j(self.J, self.Jp, 1, self.Fp, self.F, self.I)
        return Coeff*SixJ

    def TransitionStrength(self, m_F, m_Fp, F=False, Fp=False):
        if not F:
            F = self.F
        if not Fp:
            Fp = self.Fp
        Coeff = self.S_FF(m_F)*(-1)**(self.J+self.I-m_F)
        ThreeJ = wigner_3j(self.Fp, 1, self.F, m_Fp, (m_F - m_Fp), -m_F)
        return abs(Coeff*ThreeJ)
    
    def AverageFTransitionStrength(self, return_max=False):
        Strengths = np.array([])
        for m_F in np.arange(-self.F, self.F+1, 1):
            for m_Fp in np.arange(-self.Fp, self.Fp, 1):
                Strength = self.TransitionStrength(m_F, m_Fp).evalf()
                Strengths = np.append(Strengths, [Strength])
        #Strengths = np.ma.masked_equal(Strengths,0)
        Strengths = np.square(Strengths)
        ave_str = np.mean(Strengths)
        max_str = max(abs(Strengths))
        if return_max:
            return max_str
        else:
            return ave_str
    
    def AverageTransitionStrength(self, return_max=False):
        Fs = np.arange(abs(min(self.I - self.J, self.J - self.I)), self.I + self.J + 0.1, 1)
        Fps = np.arange(abs(min(self.I - self.Jp, self.Jp - self.I)), self.I + self.Jp + 0.1, 1)
        Strengths = np.array([])
        for F in Fs:
            self.F = F
            for Fp in Fps:
                self.Fp = Fp
                Strength = self.AverageFTransitionStrength()
                Strengths = np.append(Strengths, [Strength])
        ave_str = np.mean(Strengths)
        max_str = max(abs(Strengths))
        if return_max:
            return max_str
        else:
            return ave_str
    
    def TransitionFreq(self):
        return self.freq + self.freq_Off
    
    def ChangeHyperFine(self, F, Fp):
        self.F = F
        self.Fp = Fp
        
    def Add_gvert(self, Add):
        self.gvert += Add
        
#Function get_TransStrength: get the average transition strength. Input isotope (BariumTransition object), return_max=False to give the biggest transition strength
#Returns the transition strength float
def get_TransStrength(isotope, return_max=False):
    if isotope.m in (133, 135, 137):
        TransStrength = float(isotope.AverageFTransitionStrength(return_max=return_max))
    else:
        TransStrength = float(isotope.AverageTransitionStrength(return_max=return_max))
    return TransStrength

#Function listStrengths: prints a list of all of the transition strengths. Input isotopes is list of isotopes to give strengths for
def listStrengths(isotopes):
    print(f'Isotope\tAve. trans. stren.\tMax trans. stren.\tAbundance\tTotal line stren.\tTotal max line stren.')
    for isotope in isotopes:
        trans_strength = get_TransStrength(isotope)
        max_strength = get_TransStrength(isotope, maxx=True)
        abundance = isotope.abund
        if isotope.m in (133, 135, 137):
            isotope_string = f'{isotope.m}_{isotope.Fp}'
        else:
            isotope_string = f'{isotope.m}'
        print(f'{isotope_string}\t{trans_strength:0.4f}\t{max_strength:0.4f}\t{abundance*100:0.1f}%\t{trans_strength*abundance:0.4f}\t{max_strength*abundance:0.4f}')

#All of the isotopes of barium as BariumTransition objects
AtomNums = [0, 0, 1]
Ba132 = BariumTransition(132, AtomNums, Freq_Offset=167.9, Abundance=0.001, GraphVertOff=-0.025)
AtomNums = [1/2, 0, 1]
Ba133_g12 = BariumTransition(133, AtomNums, Freq_Offset=-23.3, HyperFine=[1/2, 1/2], Abundance=0.01)
AtomNums = [1/2, 0, 1]
Ba133_g32 = BariumTransition(133, AtomNums, Freq_Offset=386.65, HyperFine=[1/2, 3/2], Abundance=0.01)
AtomNums = [0, 0, 1]
Ba134 = BariumTransition(134, AtomNums, Freq_Offset=142.8, Abundance=0.0242, GraphVertOff=-0.01)
AtomNums = [3/2, 0, 1]
Ba135_12 = BariumTransition(135, AtomNums, Freq_Offset=547.3, HyperFine=[3/2, 1/2], Abundance=0.0659, GraphVertOff=0.01-0.025)
AtomNums = [3/2, 0, 1]
Ba135_32 = BariumTransition(135, AtomNums, Freq_Offset=326.7, HyperFine=[3/2, 3/2], Abundance=0.0659, GraphVertOff=-0.03)
AtomNums = [3/2, 0, 1]
Ba135_52 = BariumTransition(135, AtomNums, Freq_Offset=121.6, HyperFine=[3/2, 5/2], Abundance=0.0659, GraphVertOff=0.01)
AtomNums = [0, 0, 1]
Ba136 = BariumTransition(136, AtomNums, Freq_Offset=128.02, Abundance=0.0785)
AtomNums = [3/2, 0, 1]
Ba137_12 = BariumTransition(137, AtomNums, Freq_Offset=549.47, HyperFine=[3/2, 1/2], Abundance=0.1123, GraphVertOff=-0.025)
AtomNums = [3/2, 0, 1]
Ba137_32 = BariumTransition(137, AtomNums, Freq_Offset=274.56, HyperFine=[3/2, 3/2], Abundance=0.1123, GraphVertOff=-0.018)
AtomNums = [3/2, 0, 1]
Ba137_52 = BariumTransition(137, AtomNums, Freq_Offset=63.43, HyperFine=[3/2, 5/2], Abundance=0.1123)
AtomNums = [0, 0, 1]
Ba138 = BariumTransition(138, AtomNums, Abundance=0.717)

Isotopes133 = [Ba132, Ba133_g12, Ba133_g32, Ba134, Ba135_12, Ba135_32, \
            Ba135_52, Ba136, Ba137_12, Ba137_32, Ba137_52, Ba138]
Isotopes = [Ba132, Ba134, Ba135_12, Ba135_32, \
            Ba135_52, Ba136, Ba137_12, Ba137_32, Ba137_52, Ba138]

#Function Psat: give the saturation power of a transition. Input tau: lifetime of the upper state, lambda0: wavelength of transition, waist: beam waist (radius)
#Returns the saturation power in watts
def Psat(tau, lambda0, waist):
    I = ((2*math.pi)**2)*h_bar*c/(6*tau*lambda0**3)
    return I*math.pi*waist**2

#Function SaturationLevel: gives the saturation amount s. Input Power: laser power, Lifetime: upper state lifetime, Freq: transition freq., Waist: beam waist (radius)
#Returns the saturation amount 
def SaturationLevel(Power, Lifetime, Freq, Waist):
    wavelength = c/Freq
    Saturation_Power = Psat(Lifetime, wavelength, Waist)
    Saturation = Power/Saturation_Power
    return Saturation


class HFStructure_State:
    #level: [A, B], where A, B in MHz
    hf_ba137 = {
        #S1/2 level
        'l0j0.5': [4018.871, 0], 
        #P1/2 level
        'l1j0.5': [743.7, 0],
        #P3/2 level
        'l1j1.5': [127.2, 0],
        #D3/2 level
        'l2j1.5': [189.7296, 44.5408],
        #D5/2 level
        'l2j2.5': [-12.028, 59.533]}
    hf_ba135 = {
        #S1/2 level
        'l0j0.5': [3591.67011718, 0], 
        #P1/2 level
        'l1j0.5': [664.6, 0],
        #P3/2 level
        'l1j1.5': [113, 59],
        #D3/2 level
        'l2j1.5': [169.5898, 28.9528],
        #D5/2 level
        'l2j2.5': [-10.735, 38.392]
        }
    hf_ba133 = {
        #S1/2 level
        'l0j0.5': [-9925.45355459, 0], 
        #P1/2 level
        'l1j0.5': [-1840, 0],
        #P3/2 level - unknown
        'l1j1.5': [0, 0],
        #D3/2 level - B unknown
        'l2j1.5': [-468.5, 0],
        #D5/2 level - unknown
        'l2j2.5': [0, 0]
        }
    #Info on isotope: [hf_dict, I, gI]            gI = 0.62491/1836.13
    which_isotope = {'ba137':[hf_ba137, 3/2, 0], 'ba135':[hf_ba135, 3/2, 0], 'ba133':[hf_ba133, 1/2, 0]}
    def __init__(self, isotope, L=0, J=1/2):
        self.L = L
        self.J = J
        self.isotope = isotope
        self.which_dict, self.I, self.gI = self.which_isotope[isotope]
        self.set_transition(L=L, J=J)
    def set_F_order(self):
        I, J = self.I, self.J
        order = self.order
        Fs = np.arange(min(abs(I-J), abs(J-I)), I+J+1)
        order_F = np.zeros(order.shape)
        #mF = mI + mJ
        order_F[1,:] = order[0,:] + order[1,:]
        j = Fs.size-1
        for i, mF in enumerate(order_F[1,:]):
            if i == 0:
                mF_prev = order_F[1,i-1]
            else:
                mF_prev = order_F[1,0]
            if mF != mF_prev:
                j = Fs.size-1
            order_F[0, i] = Fs[j]
            j -= 1
        self.order_F = order_F
    def gF(self, F):
        J, I, L, gJ = self.J, self.I, self.L, self.gJ
        return gJ*(F*(F+1) + J*(J+1) - I*(I+1))/(2*F*(F+1))
                
        
    def set_transition(self, L=0, J=1/2):
        self.L = L
        self.J = J
        trans_string = f'l{int(L)}j{J:0.1f}'
        which_dict = self.which_dict
        self.A, self.B = which_dict[trans_string]
        #Lande g-factor
        self.gJ = gL + (gS-gL)*(J*(J+1) + S*(S+1) - L*(L+1))/(2*J*(J+1))
        #Dimensions of Hamiltonian Matrix
        self.hamiltonian_dim = int((2*J + 1)*(2*3/2 + 1))
        self.set_matrix_order()
        self.set_F_order()
    def set_matrix_order(self):
        I, L, J, hamiltonian_dim = self.I, self.L, self.J, self.hamiltonian_dim
        #Number of mJ's, mI's possible
        mJ_num = int(2*J + 1)
        mI_num = int(2*I + 1)
        #Organization of hamiltonian to get blocks. Row 1: mJ, Row 2: mI
        order = np.zeros([2,hamiltonian_dim])
        #Number of rows/cols in a block
        blocks = []
        #Which column of Org are we at
        column = 0
        #First loop to run at max mJ, through mI
        #Which mI to start with
        for i in range(mI_num):
            mJ = J
            mI = -I + i
            k = 0
            for j in range(mJ_num):
                #If valid combination, add to hamiltonian
                if (-J <= mJ) and (mJ <= J) and (-I <= mI) and (mI <= I):
                    # print(f'mJ:{mJ}, mI:{mI}')
                    order[0,column] = mJ
                    order[1,column] = mI
                    #This column is done
                    column += 1
                    k += 1
                #Subtract mJ, Add mI. 
                mJ -= 1
                mI += 1
            blocks.append(k)
        # print('\n')
        #Seceond loop to run at min mI through mJ
        #Which mJ to start with
        for i in range(mJ_num):
            mJ = J-i-1
            mI = -I
            k = 0
            for j in range(mI_num):
                #If valid combination, add to hamiltonian
                if (-J <= mJ) and (mJ <= J) and (-I <= mI) and (mI <= I):
                    # print(f'mJ:{mJ}, mI:{mI}')
                    order[0,column] = mJ
                    order[1,column] = mI
                    #This column is done
                    column += 1
                    k += 1
                #Subtract mJ, Add mI
                mJ -= 1
                mI += 1
            blocks.append(k)
        self.order = order
        self.blocks = blocks
    def get_eigens(self, b_field, use_blocks=False):
        hamiltonian_dim, blocks, order = self.hamiltonian_dim, self.blocks, self.order
        #Set up Hamiltonian
        hamiltonian = np.zeros([hamiltonian_dim, hamiltonian_dim])
        #num is which column are we on
        col_num = 0
        #block_evals = np.zeros(hamiltonian_dim)
        evals_all = []
        evects_all = []
        #Go through each block
        for i, block in enumerate(blocks):
            #Entry of overall matrix where block starts
            block_begin = col_num
            #... where block ends
            block_end = col_num + block
            block_matrix = np.zeros([block,block])
            #Go through the block
            for j in range(block):
                #First assign the diagonal term
                diag = self.__diagonal_term(order[0,col_num],order[1,col_num],b_field)
                hamiltonian[col_num,col_num] = diag
                block_matrix[j,j] = diag
                #Check if we can assign a PM2 term
                if (col_num - 2 >= block_begin):
                    term_pm2 = self.__pm2_term(order[0,col_num],order[1,col_num])
                    hamiltonian[col_num,col_num-2] = term_pm2
                    block_matrix[j,j-2] = term_pm2
                #Check if we can assign a PM1 term
                if (col_num - 1 >= block_begin):
                    term_pm1 = self.__pm1_term(order[0,col_num],order[1,col_num])
                    hamiltonian[col_num,col_num-1] = term_pm1
                    block_matrix[j,j-1] = term_pm1
                #Check if we can assign a MP1 term
                if (col_num + 1 < block_end):
                    term_mp1 = self.__mp1_term(order[0,col_num],order[1,col_num])
                    hamiltonian[col_num,col_num+1] = term_mp1
                    block_matrix[j,j+1] = term_mp1
                #Check if we can assign a MP2 term
                if (col_num + 2 < block_end):
                    term_mp2 = self.__mp2_term(order[0,col_num],order[1,col_num])
                    hamiltonian[col_num,col_num+2] = term_mp2
                    block_matrix[j,j+2] = term_mp2
                col_num += 1
            evals, evects = np.linalg.eig(block_matrix)
            #block_evals[block_begin:block_end] = evals
            for evalue, evect in zip(evals, evects):
                evals_all.append(evalue)
                evects_all.append(evect)
        if use_blocks:
            evals, evects = evals_all, evects_all
        else:
            [evals, evects] = np.linalg.eig(hamiltonian)
            sorted_indexes = np.argsort(np.real(evals))
            evals = evals[sorted_indexes]
            evects = evects[:,sorted_indexes]
        #Get eigenvectors and eigenvalues of the hamiltonian
        #[evects,evals] = np.linalg.eig(Hamiltonian)
        #D = eVals
        #evals = block_evals
        return np.array(evals), evects
    def __diagonal_term(self, mJ, mI, b_field):
        I, J, A, B, gJ, gI = self.I, self.J, self.A, self.B, self.gJ, self.gI
        stepMPPM = 0.25*((I*(I+1) - mI*(mI+1))*(J*(J+1) - mJ*(mJ-1)))
        stepPMMP = 0.25*((I*(I+1) - mI*(mI-1))*(J*(J+1) - mJ*(mJ+1)))
        term_a = A*mI*mJ
        #Only have term_b if not in S state and I is not 1/2
        if (J != 1/2) and (I != 1/2):
            term_b = B*(1.5*mI*mJ + 3*(mI*mI*mJ*mJ + stepMPPM + stepPMMP) - I*J*(I+1)*(J+1))/(2*I*J*(2*I-1)*(2*J-1))
        else:
            term_b = 0
        term_b_field = muB*b_field*(gJ*mJ + gI*mI)
        return term_a + term_b + term_b_field
    def __pm2_term(self, mJ, mI):
        I, J, A, B = self.I, self.J, self.A, self.B
        pm2 = 0.25*math.sqrt((I*(I+1)-mI*(mI-1))*(I*(I+1) - (mI-1)*(mI-2))*(J*(J+1)-mJ*(mJ+1))*(J*(J+1) - (mJ+1)*(mJ+2)))
        return 3*B*pm2/(2*I*J*(2*I-1)*(2*J-1))
    def __pm1_term(self, mJ, mI):
        I, J, A, B = self.I, self.J, self.A, self.B
        pm1 = 0.5*math.sqrt((J*(J+1) - mJ*(mJ+1))*(I*(I+1) - mI*(mI-1)))
        term_a = A*pm1
        if (J != 1/2) and (I != 1/2):
            term_b = B*(3/2 + 3*((mI-1)*(mJ+1) + mI*mJ))*pm1/(2*I*J*(2*I-1)*(2*J-1))
        else:
            term_b = 0
        return term_a + term_b
    def __mp1_term(self, mJ, mI):
        I, J, A, B = self.I, self.J, self.A, self.B
        mp1 = 0.5*math.sqrt((J*(J+1) - mJ*(mJ-1))*(I*(I+1) - mI*(mI+1)))
        term_a = A*mp1
        if (J != 1/2) and (I != 1/2):
            term_b = B*(3/2 + 3*((mI+1)*(mJ-1) + mI*mJ))*mp1/(2*I*J*(2*I-1)*(2*J-1))
        else:
            term_b = 0
        return term_a + term_b
    def __mp2_term(self, mJ, mI):
        I, J, A, B = self.I, self.J, self.A, self.B
        mp2 = 0.25*math.sqrt((I*(I+1)-mI*(mI+1))*(I*(I+1) - (mI+1)*(mI+2))*(J*(J+1)-mJ*(mJ-1))*(J*(J+1) - (mJ-1)*(mJ-2)))
        return 3*B*mp2/(2*I*J*(2*I-1)*(2*J-1))
    
class Transition_Laser:
    def __init__(self, Lower=HFStructure_State('ba137'), Upper=HFStructure_State('ba137', L=1, J=1/2), lower_state=6, upper_states=None, offset=0):
        self.Lower, self.Upper = Lower, Upper
        self.I = Lower.I
        self.gI = Lower.gI
        #By default, use all states
        self.lower_state, self.upper_states = lower_state, upper_states
        self.offset = offset
    def set_lowerstates_initial(self, lower_states):
        self.lower_states = lower_states
    def set_upperstates_initial(self, upper_states):
        self.upper_states = upper_states
    def get_energies(self, b_field=0):
        Lower, Upper = self.Lower, self.Upper
        lower_state, upper_states = self.lower_state, self.upper_states
        lower_energies, lower_evects = Lower.get_eigens(b_field)
        lower_energies = lower_energies[lower_state]
        upper_energies, upper_evects = Upper.get_eigens(b_field)
        if self.upper_states is not None:
            upper_energies = upper_energies[upper_states]
        return np.round(upper_energies - lower_energies - self.offset, 3), upper_evects
    def get_energies_specific(self, b_field=0):
        Lower, Upper = self.Lower, self.Upper
        lower_state, upper_states = self.lower_state, self.upper_states
        lower_energies, lower_evects = Lower.get_eigens(b_field)
        lower_energies, lower_evects = lower_energies[lower_state], lower_evects[lower_state]
        upper_energies, upper_evects = Upper.get_eigens(b_field)
        if self.upper_states is not None:
            upper_energies = upper_energies[upper_states]
            #upper_use_evects = []
            #for use in upper_states:
            #    upper_use_evects.append(upper_evects[use])
        transitions = np.round(upper_energies - lower_energies, 3)
        self.lower_evects = lower_evects
        self.upper_evects = upper_evects
        self.lower_energies = lower_energies
        self.upper_energies = upper_energies
        self.transitions = transitions
        return np.round(self.transitions - self.offset, 3)
    def spectrum_data(self, b_field):
        freqs = self.get_energies(b_field=b_field)
        min_freq, max_freq = min(freqs), max(freqs)
        x_data = np.array([])
        y_data = np.array([])
        for freq in freqs:
            x_data = np.append(x_data, [freq-1e-3, freq, freq+1e-3])
            y_data = np.append(y_data, [0, 1, 0])
        return x_data, y_data
    def getStrength(self, m, mp, F=0, Fp=0, gamma=45, phi=45):
        J, Jp = self.Lower.J, self.Upper.J
        I = self.I
        fact = np.sqrt(15*(2*Jp + 1)/4)
        total = 0
        qs = [-2, -1, 0, 1, 2]
        if I != 0:
            try:
                l = F
                lp = Fp
            except:
                print('No F, Fp given! Need these if I != 0')
        else:
            l = J
            lp = Jp
        for q in qs:
            wign = float(wigner_3j(l, 2, lp, -m, q, mp))
            geom = self.geomConstant(q, gamma, phi)
            total += wign*geom
        if I != 0:
            hf = self.hfWigner(F, Fp)
            fact *= hf
        return abs(fact*abs(total))
    def hfWigner(self, F, Fp):
        J, Jp = self.Lower.J, self.Upper.J
        I = self.I
        fact = math.sqrt((2*Fp + 1)*(2*J + 1))
        return fact*float(wigner_6j(J, Jp, 2, Fp, F, I))
    def geomConstant(self, q, gamma, phi):
        gamma_rad = gamma*math.pi/180
        phi_rad = phi*math.pi/180
        if abs(q) == 2:
            sgn = np.sign(q)
            return 1/math.sqrt(6)*abs(1/2*math.cos(gamma_rad)*math.sin(2*phi_rad) \
                                  - sgn*1j*math.sin(gamma_rad)*math.sin(phi_rad))
        elif abs(q) == 1:
            sgn = np.sign(q)
            return 1/math.sqrt(6)*abs(1j*math.sin(gamma_rad)*math.cos(phi_rad) \
                                  - sgn*math.cos(gamma_rad)*math.cos(2*phi_rad))
        elif abs(q) == 0:
            return 1/2*abs(math.cos(gamma_rad)*math.sin(2*phi_rad))
        else:
            print(f'q is an invalid value $q={q}$')
            return None