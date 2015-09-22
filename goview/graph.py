import pygal
import sys
from pygal import Config
from pygal.style import Style

class GoGraph():
	def __init__(self):
		# There should be used only class methods
		raise TypeError(self.__str___ + " could not instantiate")

	@staticmethod
	def __prepareSVGConfigGeneric(colors):
		config = Config()
		config.show_legend = True
		config.human_readable = True
		config.fill = True
		config.order_min = 0
		config.x_label_rotation = 80
		config.margin = 80
		config.legend_font_size = 10
		config.tooltip_border_radius = 10
		config.legend_font_size = 10
		config.no_data_text = "No changes found"
		config.style = Style(background='transparent',
									plot_background='#f5f5f5',
									foreground='#428bca',
									foreground_light='#000000',
									foreground_dark='#428bca',
									opacity='.6',
									opacity_hover='.9',
									transition='400ms ease-in',
									colors=colors)
		return config

	@staticmethod
	def __prepareSVGConfigTotal():
		''' Prepare pygal config to visualise changes in API '''
		config = GoGraph.__prepareSVGConfigGeneric(('#00EE00', '#EE0000'))
		config.x_title = "commit"
		config.y_title = "changes"
		return config

	@staticmethod
	def __prepareSVGConfigAdded():
		''' Prepare pygal config to visualise additions in API '''
		config = GoGraph.__prepareSVGConfigGeneric(('#00EE00', '#000000'))
		config.x_title = "commit"
		config.y_title = "added APIs"
		return config

	@staticmethod
	def __prepareSVGConfigRemoved():
		''' Prepare pygal config to visualise modifications from API '''
		config = GoGraph.__prepareSVGConfigGeneric(('#EE0000', '#00EE00'))
		config.x_title = "commit"
		config.y_title = "modified APIs"
		return config

	@staticmethod
	def __prepareSVGCPC():
		''' Prepare pygal config to visualise changes per commit API '''
		config = GoGraph.__prepareSVGConfigGeneric(('#f0ad4e', '#00EE00'))
		config.x_title = "Last N commits"
		config.y_title = "API changes"
		return config

	@staticmethod
	def makeSVGTotal(project_name, project_stats):
		''' Generate SVG stats based on changes in API '''
		line_chart = pygal.Bar(GoGraph.__prepareSVGConfigTotal())
		line_chart.title = 'API changes for ' + project_name
		line_chart.x_labels = [x['commit'][:7] for x in project_stats]
		line_chart.add('+ added', [len(x['added']) for x in project_stats])
		line_chart.add('- modified', [len(x['modified']) for x in project_stats])
		return line_chart.render()

	@staticmethod
	def makeSVGAdded(project_name, project_stats):
		''' Generate SVG stats based on additions from API '''
		line_chart = pygal.Line(GoGraph.__prepareSVGConfigAdded())
		line_chart.title = 'API additions for ' + project_name
		line_chart.x_labels = [x['commit'][:7] for x in project_stats]
		line_chart.add('+ added', [len(x['added']) for x in project_stats])
		return line_chart.render()

	@staticmethod
	def makeSVGRemoved(project_name, project_stats):
		''' Generate SVG stats based on modifications from API '''
		line_chart = pygal.Line(GoGraph.__prepareSVGConfigRemoved())
		line_chart.title = 'API modifications for ' + project_name
		line_chart.x_labels = [x['commit'][:7] for x in project_stats]
		line_chart.add('- modified', [len(x['modified']) for x in project_stats])
		return line_chart.render()

	@staticmethod
	def makeSVGCPC(project_name, project_stats, depth = 10):
		''' Generate SVG stats based on changes per commit in API '''
		line_chart = pygal.Line(GoGraph.__prepareSVGCPC())
		line_chart.title = 'API changes per commit for ' + project_name
		i = 0
		cpc = []
		for com in project_stats:
			if i == 0:
				cpc.append(len(com['modified']) + len(com['added']))
			else:
				cpc[-1] = cpc[-1] + len(com['modified']) + len(com['added'])
			i = (i + 1) % depth
		line_chart.x_labels = map(lambda x: str(x*depth + 1) + " - " + str((x+1)*10) , xrange(len(cpc) - 1, -1, -1))
		line_chart.add('CPC', cpc)
		return line_chart.render()

