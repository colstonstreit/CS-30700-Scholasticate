# Scholasticate

This is a social media-based app based around using location-based services and class similarity features to bring together students struggling with the same classes in close proximity to go from strangers to a collaborative study group. The website featured filtering and recommendation algorithms for finding similar students, pop-up notifications, and instant messaging capabilities. The goal of this app is to create a way to break the ice, allow for peers to come together, and boost academic cooperation across college campuses. We used a HTML/CSS/JS frontend along with the JS Geolocation API to display a map of all users and current public study groups, Python / Flask for backend code, and a SQLite3 database to store account and study group information about the users so user data would be persistent across log-ins.

# Running

This app requires the "flask" and "flask-login" Python modules to run, as well as SQLite3. Once downloaded, navigate to the src/ folder and run 

>python -m scholasticate

This will run the server. You can then navigate to localhost to see the site in action!
