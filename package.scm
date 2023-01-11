(use-modules (guix packages)
	(guix gexp)
	((guix licenses) #:prefix license:)
	(guix build-system python)
	(gnu packages python-web)
	(gnu packages node))

(package
	(name "Scholasticate")
	(version "0.0")
	(inputs
		`(("python-flask" ,python-flask)
		  ("python-flask-login" ,python-flask-login)))
	(native-inputs
		`(("node" ,node)))
	(propagated-inputs '())
	(source (local-file "./src" #:recursive? #t))
	(build-system python-build-system)
	(arguments `(#:phases
		(modify-phases %standard-phases
			(replace 'check
				(lambda _
					(invoke "python3" "-m" "unittest" "discover" "-v")
					(invoke "node" "js_test/run_javascript_tests.js"))))))
	(synopsis "Scholasticate: academic collaboration website")
	(description
		"Scholasticate allows students to find eachother to collaborate on homework.")
	(home-page "https://github.com/DanielBatteryStapler/Scholasticate")
	(license license:agpl3+))

