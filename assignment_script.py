import os
import re
import math

import matplotlib.pyplot as plt
import numpy as np

import directory

ST_NUM = re.compile('s[0-9]{7}')


class Assignment:
    def __init__(self, studentNumber, marker):
        self.studentNumber = studentNumber
        self.marker = marker
        self.testingGrade = 0.0
        self.qualityGrade = 0.0
        self.totalGrade = 0.0

        self.partGrades = [-1.0] * 7
        self.partComments = [[], [], [], [], [], [], []]

    def calculateQualityGrade(self):
        grade = sum(self.partGrades[0 : -1]) * self.partGrades[-1]
        grade = math.ceil(grade * 2) / 2.0
        return grade

    def __str__(self):
        sections = ['i.', 'ii.', 'iii.', 'iv.', 'v.', 'vi.', 'vii.']
        string = 'Student Number: ' + self.studentNumber + '\n'
        string += 'Testing: ' + str(self.testingGrade) + '\n'
        string += 'Quality: ' + str(self.qualityGrade) + '\n'
        for i in range(len(self.partGrades)):
            string += '  ' + sections[i] + ' ' * (6 - len(sections[i])) + str(self.partGrades[i]) + '\n'
            string += '        ' + str(self.partComments[i]) + '\n'
        return string
        




def getStudentNumber(filename):
    return filename[-12:-4]

def getMarker(filename):
    filename = filename.split('/')
    
    return filename[-3]

def getGradeFromLine(line):
    try:
        return float(line.split(':')[-1])
    except:
        return -1.0



def parseFile(filename):
    file = open(filename, 'r', encoding="utf8")
    assignment = Assignment(getStudentNumber(filename), getMarker(filename))
    partCounter = 0;

    try:
        for line in file:
            line = line.rstrip().lstrip()
            
            if (line.startswith('Testing:')):
                assignment.testingGrade = getGradeFromLine(line)
                
            elif (line.startswith('Quality:')):
                assignment.qualityGrade = getGradeFromLine(line)

            elif (line.startswith('i. ')):
                assignment.partGrades[0] = getGradeFromLine(line)
                partCounter = 0

            elif (line.startswith('ii. ')):
                assignment.partGrades[1] = getGradeFromLine(line)
                partCounter = 1

            elif (line.startswith('iii. ')):
                assignment.partGrades[2] = getGradeFromLine(line)
                partCounter = 2

            elif (line.startswith('iv. ')):
                assignment.partGrades[3] = getGradeFromLine(line)
                partCounter = 3

            elif (line.startswith('v. ')):
                assignment.partGrades[4] = getGradeFromLine(line)
                partCounter = 4

            elif (line.startswith('vi. ')):
                assignment.partGrades[5] = getGradeFromLine(line)
                partCounter = 5

            elif (line.startswith('vii. ')):
                assignment.partGrades[6] = getGradeFromLine(line)
                partCounter = 6

            elif (line == ''):
                continue

            elif (line.startswith('Code Quality Mark')):
                break

            else:
                assignment.partComments[partCounter].append(line)
    except:
        print("Error occured in parsing:", assignment.studentNumber, assignment.marker)
    return assignment




if __name__ == '__main__':
    files = []
    assignments = []
    
    for root, directories, filenames in os.walk(directory.DIR):
        for filename in filenames:
            if(ST_NUM.match(getStudentNumber(filename))): 
                files.append(os.path.join(root,filename).replace('\\', '/'))

    for file in files:
        assignments.append(parseFile(file))

    grades = dict()
    testing = []
    quality = []

    gradeCaps = [1, 1, 1, 1, 0.5, 0.5, 1]
    sections = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii']
    
    
    for assignment in assignments:
        for i in range(0, 7):
            if assignment.partGrades[i] < 0 or assignment.partGrades[i] > gradeCaps[i]:
                print('Grade error: student =', assignment.studentNumber,
                      'marker =', assignment.marker, 'section =', sections[i],
                      'grade = ', assignment.partGrades[i])
        if assignment.qualityGrade != assignment.calculateQualityGrade():
            print('Grade error: student =', assignment.studentNumber,
                  'marker =', assignment.marker, 'grade summation incorrect')
        testing.append(assignment.testingGrade)
        quality.append(assignment.qualityGrade)
        
        grades[(assignment.testingGrade, assignment.qualityGrade)] = grades.get((assignment.testingGrade, assignment.qualityGrade), 0) + 1

    plt.figure(1)

    #Plot 1: Testing-Quality Occurances
    plt.subplot(2, 2, 1)
    for grade in grades:
        plt.plot(grade[0], grade[1], 'bo', ms=(1 + 1 * grades[grade]))

    #Pass/Fail line
    x = list(np.linspace(0, 5, 11))
    y = [5 - b for b in x]
    plt.plot(x, y, 'r-')

    

    plt.xlim([-0.2, 5.2])
    plt.ylim([-0.2, 5.2])
    plt.grid(True)
    plt.xlabel('Testing Grade')
    plt.ylabel('Quality Grade')
    plt.title('Testing-Quality Graph')



    #Plot 2: Testing Grade
    plt.subplot(2, 2, 2)

    x = list(np.linspace(0, 5, 11))
    y = [testing.count(v) for v in x]

    plt.plot(x, y, 'r-')

    plt.xlim([0, 5])
    plt.ylim([0, max(y)*1.2])
    plt.grid(True)
    plt.xlabel('Testing Grade')
    plt.ylabel('Occurances')
    plt.title('Testing Grades Distribution')



    #Plot 3
    plt.subplot(2, 2, 3)

    x = list(np.linspace(0, 5, 11))
    y = [quality.count(v) for v in x]

    plt.plot(x, y, 'r-')

    plt.xlim([0, 5])
    plt.ylim([0, max(y)*1.2])
    plt.grid(True)
    plt.xlabel('Quality Grade')
    plt.ylabel('Occurances')
    plt.title('Quality Grades Distribution')


    #Plot 4
    plt.subplot(2, 2, 4)

    totalGrades = []
    for assignment in assignments:
        totalGrades.append(assignment.testingGrade + assignment.qualityGrade)

    x = list(np.linspace(0, 10, 21))
    y = [totalGrades.count(v) for v in x]

    plt.plot(x, y, 'r-')

    plt.xlim([0, 10])
    plt.ylim([0, max(y)*1.2])
    plt.grid(True)
    plt.xlabel('Grade')
    plt.ylabel('Occurances')
    plt.title('Grades Distribution')

    #plt.show()

    plt.savefig("analysis.png")
    


    

    

    
        
        








