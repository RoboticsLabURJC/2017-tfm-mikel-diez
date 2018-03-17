import yaml
import os

if __name__ == '__main__':
	with open("../calibrated_camera.yml", 'r') as stream:
		try:
			things = yaml.load(stream) 
			for value in things:
				print value
				print things[value]
		except yaml.YAMLError as exc:
			print(exc)