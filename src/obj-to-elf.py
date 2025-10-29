#!/usr/bin/python3




# -------- DEFINITIONS --------

#system
import os, sys

#subprocess
import subprocess

#current executable directory
CXP  = os.path.realpath(sys.argv[0])
CXB  = os.path.basename(CXP)
CXN  = '.'.join(CXB.split('.')[:-1])
CXD  = os.path.dirname(CXP)
pCXD = os.path.dirname(CXD)
CWD  = os.getcwd()

#paths
OUT = pCXD + "/out"
TMP = OUT  + "/tmp"






# -------- TOOLS --------

#io
def readFile(path):
	f = open(path, 'r')
	res = f.read()
	f.close()
	return res

def writeFile(path, data):
	f = open(path, 'w')
	f.write(data)
	f.close()

#output
def wrn(msg, code=1):
	header      = "[WARNING] " + CXN + ": "
	emptyHeader = ' ' * len(header)
	for l in msg.split('\n'):
		print(header + msg)
		header = emptyHeader

def err(msg, code=1):
	header      = "[ ERROR ] " + CXN + ": "
	emptyHeader = ' ' * len(header)
	for l in msg.split('\n'):
		print(header + msg)
		header = emptyHeader
	exit(code)






# -------- EXECUTION --------

#main
def main(args):



	# CMD PARSING

	#opts with their default values
	outputPath = ""
	debugMode  = False
	PICEnabled = False

	#filter opts & args
	args              = args[1:]
	args_without_opts = args[:]
	for a in range(len(args)):
		if args[a].startswith('-'):

			#help menu
			if args[a] in ("-h", "--help"):
				print("Usage: obj-to-elf [option] <src1.obj,src2.obj...> [sdl1.so.cfg,sdl2.so.cfg...]")
				print()
				print("Compile programs from OBJ format into ELF.")
				print()
				print("All given OBJ sources will be added together as it was one big file.")
				print("Same thing for the second argument (optional) which serves for external SDL linking.")
				print()
				print("Options :")
				print("  -d, --debug        : Enable debug traces.")
				print("  -p, --pic          : Compile as \"Position Independant Code\".")
				print("  -o, --output <path>: Specify output file path.")
				print("                       Default is basename of first OBJ file given, at current location,")
				print("                       and replacing extension by \".elf\".")
				print()
				print("Examples:")
				print("  obj-to-elf --debug my/dir/myFile.obj")
				print("  #Compile program my/dir/myFile.obj into myFile.elf at current location, with debug traces.")
				print()
				print("  obj-to-elf f1.obj,f2.obj,f3.obj core.sdl.cfg")
				print("  #compile the 3 input files as one, with possible external SDL link with core.sdl.")
				print()
				print("Let's Code !                                  By I.A.")
				exit(0)

			#option: debug
			elif args[a] in ("-d", "--debug"):

				#action
				debugMode = True

				#clean arg list
				args_without_opts.remove(args[a])

			#option: pic
			elif args[a] in ("-p", "--pic"):

				#action
				PICEnabled = True

				#clean arg list
				args_without_opts.remove(args[a])

			#option: output
			elif args[a] in ("-o", "--output"):
				if len(args) < a+2:
					err("n-to-obj: Missing <path> to option '-o/--output'.")

				#action
				outputPath = args[a+1]
				if os.path.isfile(outputPath):
					err("Explicit output path \"" + path + "\" refers to an existing file.\n" + \
					    "[Cancelling operation]")

				#clean arg list
				args_without_opts.remove(args[a])
				args_without_opts.remove(args[a+1])

			#undefined option
			else:
				err("Undefined option '" + args[a] + "'.")

	#args: src paths (required)
	if len(args_without_opts) == 0:
		err("Missing OBJ source input file(s).")

	#gather them as one big file
	srcSum       = ""
	srcPaths     = args_without_opts[0].split(',')
	firstSrcName = '.'.join(os.path.basename(srcPaths[0]).split('.')[:-1])
	for p in srcPaths:
		if not os.path.isfile(p):
			err("Unable to find OBJ source input file \"" + p + "\".")
		try:
			srcSum += readFile(p)
		except:
			err("Unable to read from OBJ source input file \"" + p + "\".")

	#args: sdl fp (optional)
	sdls = []
	if len(args_without_opts) > 1:
		sdls = args_without_opts[1].split(',')
		for p in sdls:
			if not os.path.isfile(p):
				err("Unable to find SDL fingerprint file \"" + p + "\".")

	#too much args
	if len(args_without_opts) > 2:
		wrn("More than 2 arguments given, they will be skipped in execution.")



	# EXECUTION

	#default outputPath
	if len(outputPath) == 0:
		outputPath = firstSrcName + ".elf"

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< C compiler used as temporary alternative
	cmd = ["gcc", "-nostdlib", "-o", outputPath, CWD + "/.obj-to-elf/tmp.c", "-L" + CWD + "/.obj-to-elf/"]

	#tmp dir
	os.system("rm -rf .obj-to-elf/")
	os.system("mkdir  .obj-to-elf/")

	#PIC
	if PICEnabled:
		cmd.append("-fPIC")

	#SDLs
	for s in sdls:
		rawName = os.path.basename(s).split('.')[0]
		cmd.append("-l" + rawName)                  #remove ALL extensions
		os.system("ln -s " + s + " " + CWD + "/.obj-to-elf/lib" + rawname + ".so")

	#src
	writeFile(".obj-to-elf/tmp.c", srcSum)

	#output path dir
	outputPath_dir = os.path.dirname(outputPath)
	if not os.path.isdir(outputPath_dir):
		os.makedirs(outputPath_dir)

	#compile
	try:
		print(' \\\n    '.join(cmd))
		p = subprocess.run(cmd, stdout=subprocess.PIPE)
		print(p.stdout.decode(), end='')
	except ImportError:
		err("Failed to compile OBJ sources to ELF, compilation errors occured.")



#run main
main(sys.argv[:])
