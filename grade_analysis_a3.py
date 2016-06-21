import os
import re
import math

import pickle

import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plot

ST_NUM = re.compile('s[0-9]{7}')
directory = "C:/Users/Joe/Dropbox/CSSE2002_2016/assignment3/a3-actualMarking/marked"
maxMarks = (6, 3, 6)

def dispHeadingUnderline(line: str):
	return '=' * len(line)

def roundValue(value: int, precision: int):
	return round(value * (1.0/precision)) / (1.0/precision)

class Marker:

	def __init__(self, name: str):
		self.name = name
		self.markedAssignments = []

	def getName(self):
		return self.name

	def addAssignment(self, assignment):
		self.markedAssignments.append(assignment)

	def __str__(self):
		return self.getName()

	def __repr__(self):
		return "<Marker {0}>".format(self.name)


class Assignment:

	def __init__(self, studentNumber: str, marker: Marker = None):
		self.maxMarks = maxMarks
		self.studentNumber = studentNumber
		self.setOverallGrade(0.0, 0.0, 0.0)
		self.marker = marker
		self.testingParts = [-1.0] * 6
		self.qualityParts = [-1.0] * 6

	def setMarker(self, marker: Marker):
		self.marker = marker

	def getMarker(self):
		return self.marker

	def setOverallGrade(self, testingGrade: float, usabilityGrade: float, qualityGrade: float):
		self.testingGrade = testingGrade
		self.usabilityGrade = usabilityGrade
		self.qualityGrade = qualityGrade

	def getStudentNumber(self):
		return self.studentNumber

	def getOverallTesting(self):
		return self.testingGrade

	def getOverallUsability(self):
		return self.usabilityGrade

	def getOverallQuality(self):
		return self.qualityGrade

	def calcTotalGrade(self):
		return self.getOverallTesting() + self.getOverallUsability() + self.getOverallQuality()

	def setTestingPart(part: int, value: int):
		self.testingParts[part] = value

	def setQualityPart(part: int, value: int):
		self.qualityParts[part] = value

	def calcOverallTesting(self):
		return sum(self.testingParts)

	def calcOverallQuality(self):
		return math.ceil(2*(sum(self.qualityParts[:5]) * self.qualityParts[5]))/2.0

	def doPartsMatchOverall(self):
		return (self.calcOverallTesting() == self.getOverallTesting()
			and self.calcOverallQuality() == self.getOverallQuality())

	def isAssignmentValid(self):
		return (self.doPartsMatchOverall()
			and (self.getOverallTesting() >= 0 and self.getOverallTesting() <= self.maxMarks[0])
			and (self.getOverallUsability() >= 0 and self.getOverallUsability() <= self.maxMarks[1])
			and (self.getOverallQuality() >= 0 and self.getOverallQuality() <= self.maxMarks[2]))

	def __str__(self):
		fmtStr = 'Student Number: {0}\nMarker: {1}\nTesting: {2} ({3})\nUsability: {4}\nQuality: {5} ({6})'
		return fmtStr.format(self.studentNumber, self.marker.getName(),
			self.getOverallTesting(), str(self.testingParts),
			self.getOverallUsability(), self.getOverallQuality(), str(self.qualityParts))

	def __repr__(self):
		return "<Assignment for {0}>".format(self.studentNumber)


class AssignmentParser:

	def __init__(self):
		self.assignments = []
		self.markers = []

	def getAssignments(self):
		return self.assignments

	def getMarkers(self):
		return self.markers

	def getStudentNumberForFile(self, filename: str):
		try:
			return filename[-12:-4]
		except:
			raise ValueError('File path did not contain a student number')

	def getMarkerForFile(self, filename: str):
		try:
			return filename.split('/')[-3]
		except:
			raise ValueError('File path did not contain a valid marker name')

	def getGradeFromLine(self, line: str):
		try:
			return float(line.split(':')[-1])
		except:
			return -1.0

	def parseAssignment(self, filename: str):
		testingPartIndicators = ['Scenario 1 [0,1]', 'Scenario 2 [0,1]', 'Scenario 3 [0,1]',
			'Scenario 4 [0,1]', 'Scenario 5 [0,1]', 'Scenario 6 [0,1]']
		qualityPartIndicators = ['i. ', 'ii. ', 'iii. ', 'iv. ', 'v. ', 'vi. ']

		testingGrade = 0.0
		usabilityGrade = 0.0
		qualityGrade = 0.0
		testingParts = [-1.0] * 6
		qualityParts = [-1.0] * 6
		assignment = Assignment(self.getStudentNumberForFile(filename))

		with open(filename, 'r', encoding="utf8") as file:
			

			for line in file:
				line = line.strip()

				if (line.startswith('Testing:')):
					testingGrade = self.getGradeFromLine(line)
				elif (line.startswith('Usability:')):
					usabilityGrade = self.getGradeFromLine(line)
				elif (line.startswith('Quality:')):
					qualityGrade = self.getGradeFromLine(line)
				else:
					for indicator in testingPartIndicators:
						if line.startswith(indicator):
							i = testingPartIndicators.index(indicator)
							testingParts[i] =self.getGradeFromLine(line)
							break

					for indicator in qualityPartIndicators:
						if line.startswith(indicator):
							i = qualityPartIndicators.index(indicator)
							qualityParts[i] = self.getGradeFromLine(line)
							break

				if line.startswith('Code Quality Mark'):
					break

		assignment.setOverallGrade(testingGrade, usabilityGrade, qualityGrade)
		assignment.testingParts = testingParts
		assignment.qualityParts = qualityParts

		return assignment

	def parseDirectoryStructure(self, dir: str):
		files = []

		for root, directories, filenames in os.walk(dir):
			for filename in filenames:
				if (ST_NUM.match(self.getStudentNumberForFile(filename))):
					files.append(os.path.join(root, filename).replace('\\', '/'))

		for file in files:
			curAssignment = self.parseAssignment(file)
			curMarkerName = self.getMarkerForFile(file)
			self.assignments.append(curAssignment)

			if curMarkerName in [marker.name for marker in self.markers]:
				# Marker already found by parser
				existingMarker = [marker for marker in self.markers if marker.name == curMarkerName][0]
				curAssignment.setMarker(existingMarker)
				existingMarker.addAssignment(curAssignment)
			else:
				# New marker
				newMarker = Marker(curMarkerName)
				curAssignment.setMarker(newMarker)
				newMarker.addAssignment(curAssignment)
				self.markers.append(newMarker)


class AssignmentAnalyser:

	def __init__(self, assignments=[], markers=[]):
		self.assignments = assignments
		self.markers = markers

	def totalGrades(self, assignmentPool):
		return [a.calcTotalGrade() for a in assignmentPool if a.isAssignmentValid()]

	def testingGrades(self, assignmentPool):
		return [a.getOverallTesting() for a in assignmentPool if a.isAssignmentValid()]

	def usabilityGrades(self, assignmentPool):
		return [a.getOverallUsability() for a in assignmentPool if a.isAssignmentValid()]

	def qualityGrades(self, assignmentPool):
		return [a.getOverallQuality() for a in assignmentPool if a.isAssignmentValid()]


	def grade3DCountDict(self, assignmentPool):
		grades = dict()

		for a in assignmentPool:
			key = (a.getOverallTesting(), a.getOverallUsability(), a.getOverallQuality())
			grades[key] = grades.get(key, 0) + 1

		return grades

	def gradeTestQualityDict(self, assignmentPool):
		grades = dict()

		for a in assignmentPool:
			key = (a.getOverallTesting(), a.getOverallQuality())
			grades[key] = grades.get(key, 0) + 1

		return grades

	def getErroneousAssignments(self, assignmentPool):
		return [a for a in assignmentPool if not a.isAssignmentValid()]

	def getOverallMin(self):
		return min(self.totalGrades(self.assignments))

	def getOverallMax(self):
		return max(self.totalGrades(self.assignments))

	def getOverallMean(self):
		return roundValue(np.mean(self.totalGrades(self.assignments)), 0.01)

	def getOverallVariance(self):
		return roundValue(np.var(self.totalGrades(self.assignments)), 0.01)

	def getOverallMedian(self):
		return roundValue(np.median(self.totalGrades(self.assignments)), 0.01)

	def overallStatDisplay(self):
		minTesting = min(self.testingGrades(self.assignments))
		meanTesting = roundValue(np.mean(self.testingGrades(self.assignments)),0.01)
		maxTesting = max(self.testingGrades(self.assignments))
		varTesting = roundValue(np.var(self.testingGrades(self.assignments)), 0.01)
		minUsability = min(self.usabilityGrades(self.assignments))
		meanUsability = roundValue(np.mean(self.usabilityGrades(self.assignments)), 0.01)
		maxUsability = max(self.usabilityGrades(self.assignments))
		varUsability = roundValue(np.var(self.usabilityGrades(self.assignments)), 0.01)
		minQuality = min(self.qualityGrades(self.assignments))
		meanQuality = roundValue(np.mean(self.qualityGrades(self.assignments)), 0.01)
		maxQuality = max(self.qualityGrades(self.assignments))
		varQuality = roundValue(np.var(self.qualityGrades(self.assignments)), 0.01)

		result = 'OVERALL ASSIGNMENT STATISTICS\n{0}\n'.format(
			dispHeadingUnderline('OVERALL ASSIGNMENT STATISTICS'))
		result += 'Total Assignments Marked: {0}\n'.format(len(self.assignments))
		result += 'Total Assignments With Marking Errors: {0}\n'.format(len(self.getErroneousAssignments(self.assignments)))
		result += 'Min/Mean/Max Grade: {0}/{1}/{2}\n'.format(self.getOverallMin(),
			self.getOverallMean(), self.getOverallMax())
		result += 'Variance: {0}\n'.format(self.getOverallVariance())
		result += 'Median: {0}\n'.format(self.getOverallMedian())
		result += '\nTesting Min/Mean/Max: {0}/{1}/{2}\tVariance: {3}\n'.format(minTesting, meanTesting, maxTesting, varTesting)
		result += 'Usability Min/Mean/Max: {0}/{1}/{2}\tVariance: {3}\n'.format(minUsability, meanUsability, maxUsability, varUsability)
		result += 'Quality Min/Mean/Max: {0}/{1}/{2}\tVariance: {3}\n'.format(minQuality, meanQuality, maxQuality, varQuality)

		return result

	def markerStatDisplay(self, markerName):
		marker = [m for m in self.markers if m.getName() == markerName][0]

		minMark = min(self.totalGrades(marker.markedAssignments))
		meanMark = np.mean(self.totalGrades(marker.markedAssignments))
		varMark = np.var(self.totalGrades(marker.markedAssignments))
		medianMark = np.median(self.totalGrades(marker.markedAssignments))
		maxMark = max(self.totalGrades(marker.markedAssignments))

		result = 'MARKER STATISTICS FOR {0}\n{1}\n'.format(marker.getName().upper(), 
			dispHeadingUnderline('MARKER STATISTICS FOR ' + marker.getName()))

		result += 'Assignments Marked: {0}\n'.format(len(marker.markedAssignments))
		result += 'Min/Mean/Max Grade: {0}/{1}/{2}\n'.format(minMark, meanMark, maxMark)
		result += 'Variance: {0}\n'.format(varMark)
		result += 'Median: {0}\n'.format(medianMark)

		return result

	def markingErrorDisplay(self):
		errorAssignments = self.getErroneousAssignments(self.assignments)

		result = 'ASSIGNMENTS WITH MARKING ERRORS\n{0}\n'.format(
			dispHeadingUnderline('ASSIGNMENTS WITH MARKING ERRORS'))

		for ea in errorAssignments:
			result += '{0} - marked by {1}\n'.format(ea.getStudentNumber(), ea.getMarker().getName())

		return result

	def dataGraph(self, assignmentPool):
		fig = plot.figure()
		gs = gridspec.GridSpec(3, 2)

		# Testing-Quality dot graph
		graph = fig.add_subplot(gs[0, 0])
		grades = self.gradeTestQualityDict(assignmentPool)
		for grade in grades:
			graph.plot(grade[0], grade[1], 'bo', ms=(1+ grades[grade]))

		graph.set_xlim([-0.2, maxMarks[0]+0.2])
		graph.set_ylim([-0.2, maxMarks[2]+0.2])
		graph.grid(True)
		graph.set_xlabel('Testing Grade')
		graph.set_ylabel('Quality Grade')
		graph.set_title('Testing-Quality Graph')

		# Testing grades

		graph = fig.add_subplot(gs[0, 1])

		x = list(np.linspace(0, maxMarks[0], maxMarks[0] * 2 + 1))
		y = [[a.getOverallTesting() for a in assignmentPool].count(v) for v in x]

		graph.set_xlim([0, maxMarks[0]])
		graph.set_ylim([0, max(y)*1.2])
		graph.grid(True)
		graph.set_xlabel('Testing Grade')
		graph.set_ylabel('Occurrences')
		graph.set_title('Testing Grades Distribution')

		graph.plot(x, y, 'r-')

		# Usability grades
		graph = fig.add_subplot(gs[1, 0])

		x = list(np.linspace(0, maxMarks[1], maxMarks[1] * 2 + 1))
		y = [[a.getOverallUsability() for a in assignmentPool].count(v) for v in x]

		graph.plot(x, y, 'r-')

		graph.set_xlim([0, maxMarks[1]])
		graph.set_ylim([0, max(y)*1.2])
		graph.grid(True)
		graph.set_xlabel('Usability Grade')
		graph.set_ylabel('Occurrences')
		graph.set_title('Usability Grades Distribution')

		# Quality grades
		graph = fig.add_subplot(gs[1, 1])

		x = list(np.linspace(0, maxMarks[2], maxMarks[2] * 2 + 1))
		y = [[a.getOverallQuality() for a in assignmentPool].count(v) for v in x]

		graph.plot(x, y, 'r-')

		graph.set_xlim([0, maxMarks[2]])
		graph.set_ylim([0, max(y)*1.2])
		graph.grid(True)
		graph.set_xlabel('Quality Grade')
		graph.set_ylabel('Occurrences')
		graph.set_title('Quality Grades Distribution')

		# Overall grades
		graph = fig.add_subplot(gs[2, :])

		x = list(np.linspace(0, sum(maxMarks), sum(maxMarks) * 2 + 1))
		y = [[a.calcTotalGrade() for a in assignmentPool].count(v) for v in x]

		graph.plot(x, y, 'r-')

		graph.set_xlim([0, sum(maxMarks)])
		graph.set_xticks(range(0, sum(maxMarks)+1, 1))
		graph.set_ylim([0, max(y)*1.2])
		graph.grid(True)
		graph.set_xlabel('Overall Grade')
		graph.set_ylabel('Occurrences')
		graph.set_title('Overall Grades Distribution')

		fig.tight_layout()
		return fig

	def overallDataGraph(self):
		return self.dataGraph(self.assignments)

	def markerDataGraph(self, markerName):
		marker = [m for m in self.markers if m.getName() == markerName][0]
		return self.dataGraph(marker.markedAssignments)

def parseArgument(user_input: str, index: int) -> str:
	splt = user_input.split(' ')
	if len(splt) > index:
		return splt[index].strip()
	else:
		return ''

if __name__ == '__main__':
	parser = AssignmentParser()
	
	print('Parsing assignments...')
	parser.parseDirectoryStructure(directory)
	print('Parsing complete!\n')

	analyser = AssignmentAnalyser(parser.getAssignments(), parser.getMarkers())

	# with open('assignments.dat', 'wb') as f:
	# 	pickle.dump(analyser, f)
	
	user_input = input('> ').strip()
	while (user_input.strip() != 'exit'):

		if user_input.startswith('show'):

			if user_input == 'show overall stats':
				print('\n')
				print(analyser.overallStatDisplay())

			elif user_input == 'show marking errors':
				print('\n')
				print(analyser.markingErrorDisplay())

			elif user_input.startswith('show assignment '):
				print('\n')
				arg = parseArgument(user_input, 2)
				if arg in [a.getStudentNumber() for a in analyser.assignments]:
					print(str([a for a in analyser.assignments if a.getStudentNumber() 
						== user_input.split(' ')[2]][0]))
					print('\n')
				else:
					print('Assignment \'{0}\' not found\n'.format(arg))

			elif user_input.startswith('show marker stats '):
				print('\n')
				arg = parseArgument(user_input, 3)
				if arg in [m.getName() for m in analyser.markers]:
					print(analyser.markerStatDisplay(arg))
				else:
					print('Marker \'{0}\' not found\n'.format(arg))

			elif user_input == 'show overall graph':
				graph = analyser.overallDataGraph()
				graph.show()

			elif user_input.startswith('show marker graph '):
				print('\n')
				arg = parseArgument(user_input, 3)
				if arg in [m.getName() for m in analyser.markers]:
					graph = analyser.markerDataGraph(arg)
					graph.show()
				else:
					print('Marker \'{0}\' not found\n'.format(arg))
		elif user_input == 'help':
			print('\nCOMMANDS\n' + dispHeadingUnderline('COMMANDS') +
				'\nshow overall stats\nshow marker stats <name>\n' +
				'show overall graph\nshow marker graph <name>\n' + 
				'show marking errors\n')
		else:
			print('Command \'{0}\' not recognised\nTry \'help\' for a command list\n'.format(user_input))


		user_input = input('> ').strip()
