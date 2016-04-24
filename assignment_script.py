import os
import re

import matplotlib.pyplot as plt
import numpy as np

DIRECTORY = "DIR"

ST_NUM = re.compile('s[0-9]{7}')


class Assignment:
    def __init__(self, studentNumber):
        self.studentNumber = studentNumber
        self.testingGrade = 0.0
        self.qualityGrade = 0.0
        self.totalGrade = 0.0

        self.partGrades = [-1.0] * 7
        self.partComments = [[], [], [], [], [], [], []]

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

def getGradeFromLine(line):
    try:
        return float(line.split(':')[-1])
    except:
        return -1.0



def parseFile(filename):
    file = open(filename, 'r')
    assignment = Assignment(getStudentNumber(filename))
    partCounter = 0;
    for line in file:
        line = line.rstrip().lstrip()
        
        if (line.startswith('Testing:')):
            assignment.testingGrade = getGradeFromLine(line)
            
        elif (line.startswith('Quality:')):
            assignment.qualityGrade = getGradeFromLine(line)

        elif (line.startswith('i.')):
            assignment.partGrades[0] = getGradeFromLine(line)
            partCounter = 0

        elif (line.startswith('ii.')):
            assignment.partGrades[1] = getGradeFromLine(line)
            partCounter = 1

        elif (line.startswith('iii.')):
            assignment.partGrades[2] = getGradeFromLine(line)
            partCounter = 2

        elif (line.startswith('iv.')):
            assignment.partGrades[3] = getGradeFromLine(line)
            partCounter = 3

        elif (line.startswith('v.')):
            assignment.partGrades[4] = getGradeFromLine(line)
            partCounter = 4

        elif (line.startswith('vi.')):
            assignment.partGrades[5] = getGradeFromLine(line)
            partCounter = 5

        elif (line.startswith('vii.')):
            assignment.partGrades[6] = getGradeFromLine(line)
            partCounter = 6

        elif (line == ''):
            continue

        elif (line.startswith('Code Quality Mark')):
            break

        else:
            assignment.partComments[partCounter].append(line)
        

    return assignment







if __name__ == '__main__':

    files = []
    assignments = []
    
    for root, directories, filenames in os.walk(DIRECTORY):
        for filename in filenames:
            if(ST_NUM.match(getStudentNumber(filename))): 
                files.append(os.path.join(root,filename).replace('\\', '/'))

    for file in files:
        assignments.append(parseFile(file))

    grades = dict()
    testing = []
    quality = []

    for assignment in assignments:
        if(assignment.partGrades[6] == -1.0):
            print(assignment.studentNumber)
        grades[(assignment.testingGrade, assignment.qualityGrade)] = grades.get((assignment.testingGrade, assignment.qualityGrade), 0) + 1

    for grade in grades:
        plt.plot(grade[0], grade[1], 'bo', ms=(2 * grades[grade]))
    

    x = list(np.linspace(0, 5, 11))
    y = [5 - b for b in x]

    plt.plot(x, y, 'r-')

    

    plt.xlim([-0.2, 5.2])
    plt.ylim([-0.2, 5.2])
    plt.xlabel('Testing Grade')
    plt.ylabel('Quality Grade')
    plt.title('Testing-Quality Graph')
    plt.grid(True)
    plt.savefig("grades.png")
    plt.show()

    

    
        
        








