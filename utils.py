import shutil
import os

# Copy file or directory
def copy(src, dst):
	if os.path.isfile(src):
		shutil.copy2(src, dst)
	elif os.path.isdir(src):
		folderName = os.path.basename(src)
		folderPath = os.path.join(dst, folderName)
		os.makedirs(folderPath, exist_ok=True)
		for fileName in os.listdir(src):
			filePath = os.path.join(src, fileName)
			copy(filePath, os.path.join(dst, folderName))