
#!/bin/bash
rm -rf *out
bash execute_jupyter_nb.sh >& execute_jupyter_nb.out
bash concatenate_files.sh >& concatenate_files.out
cd blake_nightly_data
rm -rf *out
python email_report.py >& email.out



