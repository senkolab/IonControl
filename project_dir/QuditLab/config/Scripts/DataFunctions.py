#DataFunctions.py created 2021-01-19 11:13:18.769390
import numpy as np
import sys
import time
import glob
from datetime import date
sys.path.append(r'C:\Users\ions\Documents\IonControl\scripting')
from Script import *

def GetDataFilePath(BaseDataFolder, Filename0, Temp=False, NewFile=True):
    Today = date.today()
    Year = Today.strftime("%Y")
    YearMonth = Today.strftime("%Y_%m")
    YearMonthDay = Today.strftime("%Y_%m_%d")
    if Temp:
        FilePathFinal = r"%s\%s"%(BaseDataFolder, Year)
    else:
        FilePathYear = r"%s\%s"%(BaseDataFolder, Year)
        FilePathYearMonth = r"%s\%s\%s"%(BaseDataFolder, Year, YearMonth)
        FilePathYearMonthDay = r"%s\%s\%s\%s"%(BaseDataFolder, Year, YearMonth, YearMonthDay)
        FilePathFinal = r"%s\%s\%s\%s*"%(BaseDataFolder, Year, YearMonth, YearMonthDay)
        FilePathListYear = glob.glob(FilePathYear)
        FilePathListYearMonth = glob.glob(FilePathYearMonth)
        FilePathListYearMonthDay = glob.glob(FilePathYearMonthDay)
        FilePathFinalList = glob.glob(FilePathFinal)
        if len(FilePathListYear) == 0:
            print(r"No year directory - made %s"%FilePathYear)
            os.mkdir(os.path.abspath(FilePathYear))
        if len(FilePathListYearMonth) == 0:
            print(r"No month directory - made %s"%FilePathYearMonth)
            os.mkdir(os.path.abspath(FilePathYearMonth))
        if len(FilePathListYearMonthDay) == 0:
            print(r"No day directory - made %s"%FilePathYearMonthDay)
            os.mkdir(os.path.abspath(FilePathYearMonthDay))
            FilePath0 = glob.glob(FilePathYearMonthDay)[0]
            print(FilePath0)
        else:
            FilePath0 = FilePathFinalList[0]
            print(FilePath0)
    FilenamePathFull = FilePath0 + "\\" + Filename0
    print(f'FilenamePathFull{FilenamePathFull}')
    files = glob.glob(FilenamePathFull)
    if NewFile:
        try:
            new_filenum = max([float(file.split("_")[-1].strip(".txt")) for file in files]) + 1
            print("Found %i files of this type %s already"%(new_filenum, Filename0))
        except:
            new_filenum = 1
            print("No file named %s made yet"%Filename0)
    else:
        new_filenum = 1
    Filename0 = FilenamePathFull.replace("*", "%i"%new_filenum)
    return Filename0


def SaveDataToTextFile(filename, Write ):
    filename0 = filename
    save_file = glob.glob(filename0)
    if not save_file:
        savetextfile = open(filename0,'w+')
    else:
        savetextfile = open(filename0,'a+')
    Write = '\n' + Write
    savetextfile.write(Write)
    savetextfile.close()