
import requests
import json
import sqlite3

class CourseListing:
	def __key(self):
		return (self.name, self.professor, self.title)
		
	def __eq__(self, other):
		return self.__key() == other.__key()
		
	def __hash__(self):
		return hash((hash(self.name), hash(self.professor), hash(self.title)))

def jsonRequest(filter):
	print("sending request with filter: %s" % filter)
	response = requests.get("https://api.purdue.io/odata/Courses?$expand=Subject,Classes($expand=Sections($expand=Meetings($expand=Instructors)))&$filter=" + filter, verify=False)
	#print("response: %s" % response.content.decode("utf-8"))
	return json.loads(response.content.decode("utf-8"))["value"]

def getCourses(subject):

	intervals = [
		"10000",
		"20000",
		"30000",
		"40000",
		"50000",
		"60000",
		"62500",
		"65000",
		"67500",
		"68500",
		"69000",
		"69500",
		"69800",
		"69900",
		"70000"
	]	
	
	output = jsonRequest("Subject/Abbreviation%20eq%20%27" + subject + "%27%20and%20Number%20le%20%27" + intervals[0] + "%27")
	
	for i in range(len(intervals) - 1):
		output += jsonRequest("Subject/Abbreviation%20eq%20%27" + subject + "%27%20and%20Number%20gt%20%27" + intervals[i] + "%27%20and%20Number%20le%20%27" + intervals[i + 1] + "%27")
	
	output += jsonRequest("Subject/Abbreviation%20eq%20%27" + subject + "%27%20and%20Number%20gt%20%27" + intervals[-1] + "%27")
	
	return output

def escapeSql(text):
	return text.replace("'", "''")

def deduplicateCourses(courseList):
	return list(dict.fromkeys(courseList))
	
def combineCourses(courseList):
	combinedCourseList = []
	for course in courseList:
		if(len(combinedCourseList) == 0):
			combinedCourseList.append(course)
		else:
			last = combinedCourseList[-1]
			if(last.name == course.name and last.title == course.title):
				combinedCourseList[-1].professor += "\n" + course.professor
			else:
				combinedCourseList.append(course)
	return combinedCourseList

if __name__ == "__main__":
	subjects = [
		"CS", "MSE", "MGMT", "MFET", "MET", "ME", "MCMP", "MARS", "MA", "LING", "LC", "LATN", "LALS", "LA", "KOR", "MSL", "JWST",
		"ITAL", "IT", "IPPH", "ILS", "IET", "IE", "IDIS", "IDE", "HTM", "HSOP", "HSCI", "HORT", "HONR", "HK", "JPNS", "MUS", "NRES",
		"NS", "VIP", "VCS", "TLI", "THTR", "TECH", "SYS", "STAT", "SPAN", "SOC", "SLHS", "SFS", "SCLA", "SCI", "RUSS", "REL", "REG",
		"PUBH", "NUCL", "NUPH", "NUR", "NUTR", "OBHR", "OLS", "HIST", "PES", "PHPR", "PHRM", "PHYS", "POL", "PSY", "PTGS", "PHIL",
		"HHS", "HEBR", "HDFS", "AMST", "ANSC", "ANTH", "ARAB", "ASAM", "ASEC", "ASL", "ASM", "ASTR", "AT", "BAND", "BCHM", "BIOL",
		"BME", "BMS", "BTNY", "CAND", "CPB", "COM", "CNIT", "CMPL", "CM", "CLPH", "AGRY", "CLCS", "CHM", "CHE", "CGT", "CEM", "CE",
		"CDIS", "CHNS", "VM", "AGR", "AFT", "GSLA", "GS", "GREK", "GRAD", "GER", "GEP", "FVS", "FS", "FR", "FNR", "EPCS", "ENTR",
		"ENTM", "ENGT", "ENGR", "ENGL", "ENE", "AD", "ABE", "AAS", "CSR", "DANC", "AGEC", "EAPS", "ECET", "ECON", "EDCI",
		"EDPS", "EDST", "EEE", "ECE", "WGSS", "BCM", "PTEC", "SA", "YDAE", "JOUR", "HER", "FINA", "CJUS", "EXPL", "MATH", "WOST",
		"EAS", "LCME", "BUS", "FLL", "FN", "CDFS", "LS", "CIMT", "CFS", "RECR", "HPER", "GEOL", "EDUC", "CHEM", "ENG", "AAE"
	]
	rawCourses = []
	
	print("Downloading subject data...")
	for subject in subjects:
		print("Downloading %s..." % subject)
		rawCourses = getCourses(subject)
		
		fullCourseList = []
		print("Unpacking courses...")
		for course in rawCourses:
			for course_class in course["Classes"]:
				if course_class["CampusId"] == "69fe4158-6eaf-4d27-8c81-74806f770db3":
					for section in course_class["Sections"]:
						if(section["Type"] not in ["Distance Learning", "Practice Study Observation", "Individual Study", "Recitation"]):
							for meeting in section["Meetings"]:
								for instructor in meeting["Instructors"]:
									newCourse = CourseListing()
									
									newCourse.name = course["Subject"]["Abbreviation"] + " " + course["Number"]
									newCourse.professor = instructor["Name"]
									newCourse.title = course["Title"]
									
									fullCourseList.append(newCourse)
		print("Done unpacking.")
		
		print("Deduplicating courses...")
		uniqueCourseList = deduplicateCourses(fullCourseList)
		print("Done deduplicating.")
		print("Combining courses with the same professor...")
		combinedCourseList = combineCourses(uniqueCourseList)
		print("Done combining.")
		
		if(len(combinedCourseList) > 0):
			print("Writing output to courseList_%s.sql ..." % subject)
			outputFile = open("courseList_%s.sql" % subject, "w")
			
			outputFile.write("INSERT INTO courses(school_id, course_name, professor_name, course_title) VALUES")
			for i in range(len(combinedCourseList)):
				course = combinedCourseList[i]
				outputFile.write("\n    (%s, '%s', '%s', '%s')" % ("1", escapeSql(course.name), escapeSql(course.professor), escapeSql(course.title)))
				if i < len(combinedCourseList) - 1:
					outputFile.write(",")
				else:
					outputFile.write(";")
			
			outputFile.close()
			print("Output written.")
		else:
			print("Skipping output for %s because it has no classes." % subject)
	
	print("Done downloading.")
	
	
	
	
