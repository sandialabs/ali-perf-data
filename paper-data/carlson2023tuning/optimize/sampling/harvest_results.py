import os
import subprocess

LOGDIR = "../../logs-scaling"

dirs = [d for d in os.listdir() if os.path.isdir(d)]

nrun = []; expname = []; runid = []; filenames = []
for filename in dirs:
    #name = os.path.splitext(filename)[0]
    tokens = filename.split('_')
    nrun_c = int(tokens[0][4::])
    expname_c = tokens[1]
    runid_c = tokens[2]
    nrun.append(nrun_c)
    expname.append(expname_c)
    runid.append(runid_c)
    filenames.append(LOGDIR+"/"+filename)

    if exp_name_c == "green":
        runline = "python albany_tune_RCI.py -nrun {} > {}.out".format(nrun_c, LOGDIR+"/"+filename)
        print("cd {}".format(filename))
        print(runline)
        print("cd ..")
