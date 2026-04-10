$git = "C:\Program Files\Git\cmd\git.exe"

& $git init
& $git config user.name "Nyombe"
& $git config user.email "acholkuoldeng55@gmail.com"
& $git branch -M main
& $git add .
& $git commit -m "Initial commit of Django E-Commerce application with modern UI updates"
& $git remote add origin https://github.com/Nyombe/Achol-product-store.git
& $git push -u origin main
