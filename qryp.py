import os
import sys
import time
import eggs
import shutil
import itertools
import threading
import subprocess
from cryptography.fernet import Fernet

done = False

def animation():
	global done
	for frame in itertools.cycle(["|", "/", "-", "\\"]):
		if done: break
		sys.stdout.write("\r=> " + frame)
		sys.stdout.flush()
		time.sleep(0.1)

def main():
	global done
	try:
		if sys.argv[1]:
			script = sys.argv[1]
			path = os.path.abspath(os.path.join(script, os.pardir))
			if script[-3:] == ".py" and os.path.isfile(script):
				# CREATE A TEMP FOLDER IN PARENT DIR
				try: os.mkdir(os.path.join(path, "tmp"))
				except:
					shutil.rmtree(os.path.join(path, "tmp"))
					os.mkdir(os.path.join(path, "tmp"))
				# START ANIMATION
				loading = threading.Thread(target=animation)
				loading.start()
				# TMP PYTHON SCRIPT TO EXTRACT REQUIREMENTS
				with open(os.path.join(path, "tmp", "tmp.py"), "w", encoding="utf-8") as _output:
					with open(script, "r", encoding="utf8") as _input:
						for _line in _input: _output.write(_line)
				_tmp = os.path.abspath(os.path.join(os.path.join(path, "tmp", "tmp.py"), os.pardir))
				subprocess.call("cmd /c pipreqs --encoding=utf-8 --mode=no-pin --force {dir}".format(dir = _tmp))
				with open(os.path.join(path, "tmp", "requirements.txt"), "r") as file: packages = [line.replace("\n", "") for line in file]
				if len(list(filter(None, packages))) > 0: packages = list(filter(None, packages))
				shutil.rmtree(os.path.join(path, "tmp"))
				# ENCRYPYT PYTHON SCRIPT
				with open(script, "r", encoding="utf8") as file:
					_lines = []
					tocrack = []
					for line in file:
						if line.startswith("from"): tocrack.append(line)						
						else: _lines.append(line)
					with open(os.path.join(path, "tmp"), "w") as output:
						key = Fernet.generate_key().decode()
						source = f'{"".join(tocrack)}\n{"".join(_lines)}'
						qrypted = f"""from cryptography.fernet import Fernet\nscript = '{key}.{Fernet(key).encrypt(source.encode()).decode()}'\nexec(Fernet(script.split(".")[0].encode()).decrypt(script.split(".")[1].encode()).decode())"""
						output.write(qrypted)
				# EXTRACT EGGS FROM DEPENDENCIES
				_eggs = [egg.split(" ")[1] for egg in tocrack]
				cracks = []
				for module in _eggs:
						try:
							if module.split(".")[0]: cracks.append(eggs.unpackEgg(module.split(".")[0]))
							else: cracks.append(eggs.unpackEgg(module))
						except: pass
				main_dependencies = ["'cryptography'", "'six'", "'cffi'", "'asn1crypto'", "'pycparser'"]
				for pack in cracks:
					for clean in pack: main_dependencies.append(f"'{clean}'")
				main_dependencies = ",".join(list(dict.fromkeys(main_dependencies)))
				packages = ",".join([f"'{item}'" for item in packages])
				_pack = F"{main_dependencies},{packages}".replace("''","")
				# GENERATE PY2EXE SETUP.PY 
				with open(os.path.join(path, "setup.py"), "w") as output:
					_type = "console"
					try:
						if sys.argv[2]:
							if sys.argv[2] == "windows": _type = sys.argv[2]
							else: print(f"{sys.argv[2]} is not a valid type")
					except: pass
					# WRITE OUTPUT TO SETUP.PY
					setup = "from distutils.core import setup\nimport py2exe\nsetup(\noptions = {'py2exe': {'bundle_files': 1, 'compressed': True , 'packages': [%s]} },\n%s = [{'script': '%s'}],\nzipfile = None,\n)" % (_pack, _type, os.path.basename(script))
					output.write(setup)
				# REMOVE TMP AND RENAME
				os.chdir(path)
				os.remove(os.path.basename(script))
				os.rename("tmp", os.path.basename(script))
				# STOP ANIMATION
				done = True
				loading.join()
				sys.stdout.write("FILE ENCRYPTED SUCCESSFULLY")
			# HANDLING ERRORS
			else: print("please provide a valid python file;")
	except Exception as e: print(f"INVALID PARAMS; : {e}")

if __name__ == '__main__': main()