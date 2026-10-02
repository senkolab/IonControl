#DataFunctions.py created 2021-01-19 11:13:18.769390
import numpy as np
import pandas as pd
import math
import sys
import time
import glob
from PIL import Image
from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\scripting')
from Script import *
import http.client
from Functions_Measurement import set_global_value
#Add the following line to package the script functions to easily send to these functions
#script_functions = (getGlobal, setGlobal, setScan, startScan, stopScan, getAllData)

#Function GetDataFilePath: Get the folder for today's date from within the lab data storage file-server. Input filename0, BaseDataFolder=r"Z:\Lab Data\Sessions", 
#NewFile=True is for specifying to create a brand new file, even if one already exists. Temp=False is for testing. 
#Returns a tuple of the full filename0 path, and the folder path
def GetDataFilePath(filename0, BaseDataFolder=r"Z:\Lab Data\Sessions", NewFile=True, Temp=False):
    Today = date.today()
    Year = Today.strftime("%Y")
    YearMonth = Today.strftime("%Y_%m")
    YearMonthDay = Today.strftime("%Y_%m_%d")
    if Temp:
        FilePathFinal = r"%s\%s"%(BaseDataFolder, Year)
    else:
        #Setup the different layers of folders
        FilePathYear = r"%s\%s"%(BaseDataFolder, Year)
        FilePathYearMonth = r"%s\%s\%s"%(BaseDataFolder, Year, YearMonth)
        FilePathYearMonthDay = r"%s\%s\%s\%s"%(BaseDataFolder, Year, YearMonth, YearMonthDay)
        FilePathFinal = r"%s\%s\%s\%s*"%(BaseDataFolder, Year, YearMonth, YearMonthDay)
        #Check whether each deeper layer has been made yet
        FilePathListYear = glob.glob(FilePathYear)
        FilePathListYearMonth = glob.glob(FilePathYearMonth)
        FilePathListYearMonthDay = glob.glob(FilePathYearMonthDay)
        #If no year directory made yet, make it
        if len(FilePathListYear) == 0:
            print(r"No year directory - made %s"%FilePathYear)
            os.mkdir(os.path.abspath(FilePathYear))
        #If no ...
        if len(FilePathListYearMonth) == 0:
            print(r"No month directory - made %s"%FilePathYearMonth)
            os.mkdir(os.path.abspath(FilePathYearMonth))
        if len(FilePathListYearMonthDay) == 0:
            print(r"No day directory - made %s"%FilePathYearMonthDay)
            os.mkdir(os.path.abspath(FilePathYearMonthDay))
            FilePath0 = glob.glob(FilePathYearMonthDay)[0]
        FilePathFinalList = glob.glob(FilePathFinal)
        FilePath0 = FilePathFinalList[0]
    #Add filename to the path
    FilePathFull = FilePath0 + "\\"
    FilenamePathFull = FilePathFull + filename0
    print(f'FilenamePathFull: {FilenamePathFull}')
    files = glob.glob(FilenamePathFull)
    #If making new file, set name with incremented number
    if NewFile:
        try:
            new_filenum = max([float(file.split("_")[-1].strip(".txt")) for file in files]) + 1
            print("Found %i files of this type %s already"%(new_filenum, filename0))
        except:
            new_filenum = 1
            print("No file named %s made yet"%filename0)
    else:
        new_filenum = 1
    FilenamePathFull = FilenamePathFull.replace("*", "%i"%new_filenum)
    return FilenamePathFull, FilePathFull

#Function makeRelativeDirectory: Create a directory relative to the current filepath. Input filepath (full path), directory='new folder'
#Returns the new directory full filepath
def makeRelativeDirectory(filepath, directory='new folder'):
    filepath_new = filepath + directory
    #Check if the new directory exists already
    filepath_new_check = glob.glob(filepath_new)
    if len(filepath_new_check) == 0:
        print(f"No directory - made {filepath_new}")
        os.mkdir(os.path.abspath(filepath_new))
        filepath = glob.glob(filepath + directory)[0]
    else:
        print(f"Directory {filepath_new_check} already exists")
        filepath = filepath_new_check[0]
    return filepath
    
#Function SaveDataToTextFile: saves text data to the file. Input filename (full path), and text_write
#Returns nothing, just saves the data
def SaveDataToTextFile(filename, text_write):
    filename0 = filename
    save_file = glob.glob(filename0)
    #If file doesn't exist yet, write it, otherwise append to new line
    if not save_file:
        savetextfile = open(filename0,'w+')
    else:
        savetextfile = open(filename0,'a+')
        text_write = '\n' + text_write
    savetextfile.write(text_write)
    savetextfile.close()

#Function GetRawDataFolder: gets the folder where today's IonControl program pulse program and scan data are saved
#Returns the filepath of the current folder
def GetRawDataFolder():
    BaseFilePath = r'C:\Users\ions\Documents\IonControl\project_dir\QuditLab'
    todaydate = date.today()
    filepath0 = BaseFilePath + '\\' + todaydate.strftime("%Y") + '\\' + todaydate.strftime("%Y_%m") + '\\' + todaydate.strftime("%Y_%m_%d")
    return filepath0

#Function GetRawData: gets the raw data from the last x files saved. Input filename: the full filepath of the file name type, last=1: how many of the last files to get
#Returns data: all of the data from the files in an array, either 1D or 2D depending on how many files to consider
def GetRawData(filename, last=1):
    Filepath = GetRawDataFolder()
    files = glob.glob(Filepath + "\\" + filename + "*")
    files = files[-last:]
    data = pd.read_csv(files[0], delimiter = "[\],\[\t]", engine='python', header=None)
    data = np.asarray(data)
    if len(files) > 1:
        for i, data_file in enumerate(files):
            if i == 0:
                continue
            data_next = pd.read_csv(data_file, delimiter = "[\],\[\t]", engine='python', header=None)
            data_next = np.asarray(data_next)
            data = np.vstack((data, data_next))
    return data

def getData_xmlFile(files0, data_index_x=2, data_index_y=7, skiprows=74):
    for i in range(files0.size):
        data = pd.read_csv(files0[i], delimiter = "\[|\]|,|\"|\t", engine='python',header=None, skiprows=skiprows).values
        data = data[:, [data_index_x, data_index_y]]
        if i == 0:
            experiments, points = data.shape
            data_all = np.zeros([len(files0), experiments, points])
        data_all[i, :, :] = data
    return data_all

def getData_1762_Calib(files0):
    for i in range(files0.size):
        data = pd.read_csv(files0[i], delimiter = "\[|\]|,|\"|\t", engine='python',header=None).values
        #print(data)
        #data = data.T
        if i == 0:
            data_all = []
        data_all.append(data)
    return np.array(data_all)

def linear_fit(x, slope, offset):
    return slope*x + offset

def poly_fit(x, a1, a2, a3, amp):
    return (a1*x + a2*x**2 + a3*x**3)/amp

#Function acquireBlackflyFrame: gets the current image from the blackfly camera frame. Input filepath specifies where the blackfly program should save the file to, address=r"192.168.168.47:8081" is the IP address of the camera
#Returns the image, a success code, and the query data
def acquireBlackflyFrame(filepath, address=r"192.168.168.47:8081"):
    filepath = filepath.replace(" ", "%20")
    query = address + "?requesttype=acquire"
    query += "&filepath=" + filepath
    connection = http.client.HTTPConnection(address, timeout = 30)
    connection.request("GET", query)
    reply = connection.getresponse()
    data = reply.read()
    data = data.decode('utf-8')
    print("Status is: ", reply.status, " Reason is: ", reply.reason)
    print_statement, Success = data.split('\t')
    Success = bool(Success)
    print(print_statement)
    connection.close()
    filepath = filepath.replace("%20"," ")
    files = glob.glob(os.path.abspath(filepath))
    im = Image.open(files[0])
    im_array = np.array(im)
    im.close()
    return im_array,Success,data

#Function GetNumberOfIons: figure out how many ions are in the trap based on an image array. Input A: 2D image array, multiplier: what to multiply by in calculating bright threshold
#Returns number_of_ions and peak_positions
def GetNumberOfIons(A,multiplier):
    [max_y_ind,max_x_ind]=np.where(A == np.amax(A))
    #B = np.sum(A,axis=0)/np.size(A,axis=0)
    B = A[max_y_ind,:]
    B = B[0]
    [peak_positions,local_peaks] = find_peaks(B)
    #[peak_positions,local_peaks] = find_peaks(A[int(max_y_ind[0]),xmin:xmax])
    threshold = np.percentile(A,50) + multiplier*(np.percentile(A,95)-np.percentile(A,50))
    peak_positions_th = peak_positions[local_peaks > threshold]
    peak_positions_th = peak_positions_th.astype(float)
    if len(peak_positions_th) > 1:
        peak_positions_th_diff = peak_positions_th[1:]-peak_positions_th[0:-1]
        peak_positions_th_diff_end0 = np.append(peak_positions_th_diff,0)
        peak_positions_th_diff_start0 = np.append(0,peak_positions_th_diff)
        peak_positions_th[peak_positions_th_diff_end0 == 1] = peak_positions_th[peak_positions_th_diff_end0 == 1] + 0.5
        index = np.asarray(range(0,len(peak_positions_th)))
        peak_positions_th = np.delete(peak_positions_th,index[peak_positions_th_diff_start0 == 1])
    number_of_ions = len(peak_positions_th)
    return number_of_ions,peak_positions_th

#Function find_peaks: looks for all peaks in the image. Input in_array is 2D image
#Returns peak_positions and peaks
def find_peaks(in_array):
    in_array = in_array.astype(float)
    a = in_array[1:-1] - in_array[0:-2]
    b = in_array[1:-1] - in_array[2:]
    index = (a>=0) & (b>=0)
    index = np.append(np.insert(index,False,0),False)
    local_peaks = in_array[index]
    c = np.asarray(range(0,len(in_array)))
    peak_positions = c[index]
    return [peak_positions,local_peaks]

#Function GetPumpedIndicator: 
def GetPumpedIndicator(PMT_Count):
    PMT_Count = np.array(PMT_Count)
    PMT_Count_Sorted = PMT_Count.flatten()
    PMT_Count_Sorted = np.sort(PMT_Count_Sorted)
    if len(PMT_Count_Sorted) > 1000:
        index_skip = int(len(PMT_Count_Sorted)/1000)
    else:
        index_skip = 1
    PMT_Count_Sorted_Skip = PMT_Count_Sorted[0:-1:index_skip]
    PMT_Count_Diff = PMT_Count_Sorted_Skip[1:-1] - PMT_Count_Sorted_Skip[0:-2]
    PMT_Count_Diff_max = max(PMT_Count_Diff)
    if np.size(PMT_Count_Diff_max)>1:
        PMT_Count_Diff_max = PMT_Count_Diff_max[0]
    PMT_Count_Diff_max_ind = np.where(PMT_Count_Diff == max(PMT_Count_Diff))
    PMT_Count_Diff_max_ind = PMT_Count_Diff_max_ind[0][0]
    #if np.size(PMT_Count_Diff_max_ind)>1:
    #    PMT_Count_Diff_max_ind = PMT_Count_Diff_max_ind[0][0]
    PMT_Threshold = PMT_Count_Sorted_Skip[PMT_Count_Diff_max_ind] + PMT_Count_Diff_max/2
    Pumped_Indicator = np.zeros(np.shape(PMT_Count))
    Pumped_Indicator[PMT_Count<PMT_Threshold] = 1
    return Pumped_Indicator

#Function getShelvingThreshold: gets the threshold between a bright and dark ion,. Input counts is an array of counts, any dimension, which has data from both bright and dark ions
#Returns threshold: a floating point value which is optimized to be the cutoff for deciding if an ion is bright or dark
def getShelvingThreshold(counts):
    data_sorted = np.sort(counts, axis=None)
    if len(data_sorted) > 1000:
        data_sorted = data_sorted[0:-1:round(data_sorted.size/1000)]
    data_sorted_diff = data_sorted[1:-1] - data_sorted[0:-2]
    data_diff_max = max(data_sorted_diff)
    data_diff_maxind = np.argmax(data_sorted_diff)
    threshold = data_diff_max/2 + data_sorted[data_diff_maxind]
    return threshold

#Function cleanDataShelve614Repump: picks experiments where successfully shelved, calculates if it was repumped after, and returns the averate prob. of repumping. Input data_shelves, data_repumps, both arrays of the same shape
#Returns data_means, data_vars, data_totals, which tell you the averate repumping success rate, the variation, and the total number of experiments
def cleanDataShelve614Repump(data_shelves, data_repumps):
    threshold = getShelvingThreshold(data_shelves)
    print(f'dark threshold: {threshold}')
    if data_shelves.shape[0] == 1:
        data_repump = data_repumps[data_shelves<=threshold]
        data_repump = data_repump > threshold
        data_means = np.mean(data_repump)
        data_vars = np.std(data_repump)/np.sqrt(data_repump.size)
        data_totals = 1
    else:
        data_means = np.zeros((data_shelves.shape[0]))
        data_vars = np.zeros((data_shelves.shape[0]))
        data_totals = np.zeros((data_shelves.shape[0]))
        for i, data_shelve in enumerate(data_shelves):
            data_repump = data_repumps[i]
            data_repump = data_repump[data_shelve<=threshold]
            data_repump = data_repump > threshold
            data_means[i] = np.mean(data_repump)
            data_vars[i] = np.std(data_repump)/np.sqrt(data_repump.size)
            data_totals[i] = data_repump.size
    return data_means, data_vars, data_totals


def setGlobalPulseTimeScan(start_time, stop_time, time_step, script_functions):
    getGlobal, setGlobal, setScan, startScan, stopScan, getAllData = script_functions
    set_global_value("PulseTimeStart", start_time, "us", script_functions)

    set_global_value("PulseTimeStop", stop_time, "us", script_functions)

    set_global_value("PulseTimeStep", time_step, "us", script_functions)

def Get_1762_Latest_EOM_Freqs(want_array):
    #Input definition:
    #want_array: a list of sets of 3 numbers e.g. [[2,2,0],[-1,4,-4]], which defines 
    #the desired S to D EOM transition frequency. The first number denotes the 
    #m number in the S level, the second number denotes the F number in the D level,
    #the third number denotes the m number in the D level.
    #
    #Output definition:
    #Freqs: a 1D array of numbers, of the same length as the list in want_array.
    #Returns the latest measured frequencies in MHz of the transitions dictated
    #in want_array.
    freqs_latest = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Post_processing_PJ\\Figures\\Linear_Regression\\Freqs_latest.txt")
    m_S_num_list = np.asarray([-2,-1,0,1,2])
    F_num_list = np.asarray([1,1,1,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4])
    m_D_num_list = np.asarray([1,0,-1,2,1,0,-1,-2,3,2,1,0,-1,-2,-3,4,3,2,1,0,-1,-2,-3,-4])
    Freqs = np.empty(np.size(want_array,0))
    ind_count = 0
    for want_index in want_array:
        m_S_num = want_index[0]
        F_num = want_index[1]
        m_D_num = want_index[2]
        Freqs[ind_count] = freqs_latest[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]
        ind_count += 1
    return Freqs    

def Get_1762_PiTimes(want_array,pitime_n2,pitime_n1,pitime_0,pitime_p1,pitime_p2):
    #Input definition:
    #want_array: a list of sets of 3 numbers e.g. [[2,2,0],[-1,4,-4]], which defines 
    #the desired S to D EOM transition frequency. The first number denotes the 
    #m number in the S level, the second number denotes the F number in the D level,
    #the third number denotes the m number in the D level.
    #pitime_XX: scalar number of the pi times for the reference XX transitions in us, where
    #XX is delta_m, ranging from negative 2 to positive 2.
    #
    #Output definition:
    #PiTimes: a 1D array of numbers, of the same length as the list in want_array.
    #Returns the estimated pi pulse times in us using scaling parameter of the transitions dictated
    #in want_array.
    a_pitime = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Calibration_Parameters\\PiTime_scale_param.txt")
    m_S_num_list = np.asarray([-2,-1,0,1,2])
    F_num_list = np.asarray([1,1,1,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4])
    m_D_num_list = np.asarray([1,0,-1,2,1,0,-1,-2,3,2,1,0,-1,-2,-3,4,3,2,1,0,-1,-2,-3,-4])
    PiTimes = np.empty(np.size(want_array,0))
    ind_count = 0
    for want_index in want_array:
        m_S_num = want_index[0]
        F_num = want_index[1]
        m_D_num = want_index[2]
        if m_S_num == 0 and F_num == 0 and  m_D_num == 0:
            print('this triggered')
            PiTimes[ind_count] = 1e6
        else:
            delta_m = m_D_num - m_S_num
            if delta_m == -2:
                pitime_ref = pitime_n2
            elif delta_m == -1:
                pitime_ref = pitime_n1
            elif delta_m == 0:
                pitime_ref = pitime_0
            elif delta_m == 1:
                pitime_ref = pitime_p1
            elif delta_m == 2:
                pitime_ref = pitime_p2
            else:
                print("delta m out of range")
                return
            PiTimes[ind_count] = a_pitime[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]*pitime_ref
        ind_count += 1
    return PiTimes
x = Get_1762_PiTimes([[0,0,0]],0,0,0,0,0)
print(x)
def Get_1762_EOM_Freqs(want_array,f_offset,f_upper):
    #Input definition:
    #want_array: a list of sets of 3 numbers e.g. [[2,2,0],[-1,4,-4]], which defines 
    #the desired S to D EOM transition frequency. The first number denotes the 
    #m number in the S level, the second number denotes the F number in the D level,
    #the third number denotes the m number in the D level.
    #f_offset: scalar number of the offset transition EOM frequency used for the an1 and an2 estimation in MHz.
    #f_upper: scalar number of the upper transition EOM frequency used for the an1 and an2 estimation in MHz.
    #
    #Output definition:
    #Freqs: a 1D array of numbers, of the same length as the list in want_array.
    #Returns the estimated frequencies in MHz using an1 and an2 of the transitions dictated
    #in want_array.
    BFieldSensitivity_table = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Post_processing_PJ\\Figures\\Linear_Regression\\BFieldSensitivity_table.txt")
    BSensitivityScale = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Post_processing_PJ\\Figures\\Linear_Regression\\BSensitivityScale.txt")
    m_S_num_list = np.asarray([-2,-1,0,1,2])
    F_num_list = np.asarray([1,1,1,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4])
    m_D_num_list = np.asarray([1,0,-1,2,1,0,-1,-2,3,2,1,0,-1,-2,-3,4,3,2,1,0,-1,-2,-3,-4])
    Freqs_table = np.empty([np.size(an2_global_table,0),np.size(an2_global_table,1)])



    for D_index in range(np.size(an2_global_table,0)):
       for S_index in range(np.size(an2_global_table,1)):
            Freqs_table[D_index,S_index] = BSensitivityScale*BFieldSensitivity_table[D_index,S_index]*(f_upper - f_offset) + an2_global_table[D_index,S_index] + f_offset            
    
    
    
    Freqs_S_diff = np.nanmean(Freqs_table[:,1:] - Freqs_table[:,0:-1],0)
    S_Freq_Shifts = np.empty([np.size(Freqs_table,1),np.size(Freqs_table,1)])
    
    for S_index in range(np.size(an2_global_table,1)):
        for neg_index in range(S_index+1):
            if neg_index == S_index:
                S_Freq_Shifts[S_index,neg_index] = 0
            else:
                S_Freq_Shifts[S_index,neg_index] = np.sum(Freqs_S_diff[neg_index:S_index])
        for pos_index in range(S_index+1,np.size(an2_global_table,1)):
            if pos_index == S_index:
                S_Freq_Shifts[S_index,pos_index] = 0
            else:
                S_Freq_Shifts[S_index,pos_index] = -np.sum(Freqs_S_diff[S_index:pos_index])
                
    for D_index in range(np.size(an2_global_table,0)):
        for S_index in range(np.size(an2_global_table,1)):
            if np.isnan(Freqs_table[D_index,S_index]):
                Freqs_table[D_index,S_index] = np.nanmean(Freqs_table[D_index,:] + S_Freq_Shifts[S_index,:])
                
    Freqs = np.empty(np.size(want_array,0))
    ind_count = 0
    for want_index in want_array:
        m_S_num = want_index[0]
        F_num = want_index[1]
        m_D_num = want_index[2]
        Freqs[ind_count] = Freqs_table[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]
        #Freqs[ind_count] = an1[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]* \
        #(f_upper - f_offset) \
        #+ an2[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)] \
        #+ f_offset
        ind_count += 1
    return Freqs 

def Get_1762_EOM_Freqs_an1an2(want_array,f_offset,f_upper):
    #Input definition:
    #want_array: a list of sets of 3 numbers e.g. [[2,2,0],[-1,4,-4]], which defines 
    #the desired S to D EOM transition frequency. The first number denotes the 
    #m number in the S level, the second number denotes the F number in the D level,
    #the third number denotes the m number in the D level.
    #f_offset: scalar number of the offset transition EOM frequency used for the an1 and an2 estimation in MHz.
    #f_upper: scalar number of the upper transition EOM frequency used for the an1 and an2 estimation in MHz.
    #
    #Output definition:
    #Freqs: a 1D array of numbers, of the same length as the list in want_array.
    #Returns the estimated frequencies in MHz using an1 and an2 of the transitions dictated
    #in want_array.
    an1 = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Calibration_Parameters\\an1_2026_ms0.txt")
    an2 = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Calibration_Parameters\\an2_2026_ms0.txt")
    m_S_num_list = np.asarray([-2,-1,0,1,2])
    F_num_list = np.asarray([1,1,1,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4])
    m_D_num_list = np.asarray([1,0,-1,2,1,0,-1,-2,3,2,1,0,-1,-2,-3,4,3,2,1,0,-1,-2,-3,-4])
    Freqs_table = np.empty([np.size(an1,0),np.size(an1,1)])

    for D_index in range(np.size(an1,0)):
        for S_index in range(np.size(an1,1)):
            Freqs_table[D_index,S_index] = an1[D_index,S_index]*(f_upper - f_offset) + an2[D_index,S_index] + f_offset            
    
    Freqs_S_diff = np.nanmean(Freqs_table[:,1:] - Freqs_table[:,0:-1],0)
    S_Freq_Shifts = np.empty([np.size(Freqs_table,1),np.size(Freqs_table,1)])
    
    for S_index in range(np.size(an1,1)):
        for neg_index in range(S_index+1):
            if neg_index == S_index:
                S_Freq_Shifts[S_index,neg_index] = 0
            else:
                S_Freq_Shifts[S_index,neg_index] = np.sum(Freqs_S_diff[neg_index:S_index])
        for pos_index in range(S_index+1,np.size(an1,1)):
            if pos_index == S_index:
                S_Freq_Shifts[S_index,pos_index] = 0
            else:
                S_Freq_Shifts[S_index,pos_index] = -np.sum(Freqs_S_diff[S_index:pos_index])
                
    for D_index in range(np.size(an1,0)):
        for S_index in range(np.size(an1,1)):
            if np.isnan(Freqs_table[D_index,S_index]):
                Freqs_table[D_index,S_index] = np.nanmean(Freqs_table[D_index,:] + S_Freq_Shifts[S_index,:])
                
    Freqs = np.empty(np.size(want_array,0))
    ind_count = 0
    for want_index in want_array:
        m_S_num = want_index[0]
        F_num = want_index[1]
        m_D_num = want_index[2]
        if m_S_num == 0 and F_num == 0 and  m_D_num == 0:
            Freqs[ind_count] = 800
        else:
            Freqs[ind_count] = Freqs_table[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]
        #Freqs[ind_count] = an1[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]* \
        #(f_upper - f_offset) \
        #+ an2[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)] \
        #+ f_offset
        ind_count += 1

            
    return Freqs 

def Get_1762_Latest_PiTimes(want_array):
    #Input definition:
    #want_array: a list of sets of 3 numbers e.g. [[2,2,0],[-1,4,-4]], which defines 
    #the desired S to D EOM transition frequency. The first number denotes the 
    #m number in the S level, the second number denotes the F number in the D level,
    #the third number denotes the m number in the D level.
    #
    #Output definition:
    #Freqs: a 1D array of numbers, of the same length as the list in want_array.
    #Returns the latest measured pi pulse times in us of the transitions dictated
    #in want_array.
    pitimes_latest = np.loadtxt("Z:\\Lab Data\\D52_Calibration_Ba137\\Post_processing_PJ\\Figures\\Linear_Regression\\PiTime_latest.txt")
    m_S_num_list = np.asarray([-2,-1,0,1,2])
    F_num_list = np.asarray([1,1,1,2,2,2,2,2,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4])
    m_D_num_list = np.asarray([1,0,-1,2,1,0,-1,-2,3,2,1,0,-1,-2,-3,4,3,2,1,0,-1,-2,-3,-4])
    PiTimes = np.empty(np.size(want_array,0))
    ind_count = 0
    for want_index in want_array:
        m_S_num = want_index[0]
        F_num = want_index[1]
        m_D_num = want_index[2]
        PiTimes[ind_count] = pitimes_latest[np.where((F_num_list == F_num) & (m_D_num_list == m_D_num)),np.where(m_S_num_list == m_S_num)]
        ind_count += 1
    return PiTimes    