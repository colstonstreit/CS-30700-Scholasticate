from setuptools import setup

setup(
	name='scholasticate',
	version='0.0',
	url='https://github.com/DanielBatteryStapler/Scholasticate',
	license='AGPL',
	packages=['scholasticate', 'scraper'],
	package_data={'scholasticate': ['templates/*', 'static/*', 'static/css/*', 'static/img/*']},
	include_package_data=True,
	entry_points = {
		'console_scripts': [
			'scholasticate = scholasticate.__main__:main',
		]
	}
)

