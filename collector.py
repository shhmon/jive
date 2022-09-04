from os import listdir, path, makedirs
import re
import sys
import gzip
import shutil
import xml.etree.ElementTree as ET
from utils import copy

PATH_TYPE_MISSING 	= '0'
PATH_TYPE_EXTERNAL 	= '1'
PATH_TYPE_LIBRARY 	= '2'
PATH_TYPE_PROJECT 	= '3'

REL_SAMPLE_LOCATION = 'Samples/Imported/'
REGEX_PATTERN = r'^(\/.+\/)*((.+)\.(.+))$'

SUPPORTED = [11, 10]

class Collector:

	def __init__(self, target: str):
		self.content = [f for f in listdir(target) if '.als' not in f]
		self.liveSets = [f for f in listdir(target) if '.als' in f]
		self.projPath = target if target[-1] == '/' else (target + '/')
		self.sampPath = path.join(self.projPath + REL_SAMPLE_LOCATION)
	
	# Push the contents of project to out
	def push(self, out: str):
		for file in self.content:
			filePath = path.join(self.projPath, file)
			if (filePath != out and file[0] != '.'):
				copy(filePath, out)
		
		for lset in self.liveSets:
			alsPath = path.join(self.projPath, lset)
			xmlPath = path.join(out, f'{lset}.xml')
			etree = ET.parse(gzip.GzipFile(alsPath))
			etree.write(xmlPath)

	def collect_project(self):
		for liveSet in self.liveSets:
			self.collect_live_set(liveSet)
	
	def collect_live_set(self, setName: str):
		setPath = path.join(self.projPath, setName)
		# Open file and verify version
		with gzip.open(setPath, 'r') as f:
			root = ET.parse(f).getroot()
			f.close()

		version = int(root.attrib['MinorVersion'][:2])
		
		if version not in SUPPORTED:
			raise Exception(f'Live {version} is not supported by the collector')

		# Get all file references
		filerefs = [r.find("FileRef") for r in root.iter('SampleRef')]

		# Handle the references
		for ref in filerefs:
			self.handle_reference(ref, version)

		# Save the live set		
		content = ET.tostring(root, encoding='utf8', method='xml')
		with gzip.open(setPath, 'w') as f:
			f.write(content)
			f.close()

		print(f'Collected {setName}')

	def handle_reference(self, ref: str, version: int):
		pathType = ref.find("RelativePathType")

		if pathType.attrib['Value'] == PATH_TYPE_EXTERNAL:
			relaPath = ref.find("RelativePath")

			if version == 11:
				truePath = ref.find("Path")
				filePath = truePath.attrib["Value"]
				fileName = re.match(REGEX_PATTERN, filePath).group(2)

				# Update references
				truePath.set('Value', path.join(self.sampPath, fileName))
				relaPath.set('Value', path.join(REL_SAMPLE_LOCATION, fileName))
			
			# TODO: Exchange string concat paths to path.join
			elif version == 10:
				# Construct path from relative path elements
				filePath = self.projPath[:-1]
				fileName = ref.find('Name').attrib['Value']
				relpElem = [e for e in relaPath.iter('RelativePathElement')]

				for element in relpElem:
					value = element.attrib['Dir']
					filePath += '/' + (value if value else '..')
					relaPath.remove(element)
				
				filePath += '/' + fileName

				# Update references
				ET.SubElement(relaPath, 'RelativePathElement', attrib={'Dir': 'Samples', 'Id': str(len(relpElem)) })
				ET.SubElement(relaPath, 'RelativePathElement', attrib={'Dir': 'Imported', 'Id': str(len(relpElem) + 1) })

				# Update the PathHint references (not sure if needed)
				pathHint = ref.find("SearchHint").find("PathHint")
				relpElem = [e for e in pathHint.iter('RelativePathElement')]

				for element in relpElem:
					pathHint.remove(element)

				dirList = self.projPath.split('/')[1:-1] + ['Samples', 'Imported']
				for i, _dir in enumerate(dirList):
					ET.SubElement(pathHint, 'RelativePathElement', attrib={'Dir': _dir, 'Id': str(len(relpElem) + i) })
			
			else:
				return
			
			pathType.set('Value', PATH_TYPE_PROJECT)
			print(f'Copying external sample: {filePath}')
			self.copy_sample(filePath)
			
	# Copy file to local sample folder
	def copy_sample(self, src: str):
		makedirs(self.sampPath, exist_ok=True)
		shutil.copy2(src, self.sampPath)
			
if __name__ == "__main__":
	name = sys.argv[1]
	coll = Collector(name)
	coll.collect_project()
