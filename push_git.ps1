$git = "C:\Program Files\Git\cmd\git.exe"

& $git checkout --ours README.md
& $git add README.md
& $git commit -m "Resolved merge conflict on README.md"
& $git push -u origin main
