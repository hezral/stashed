pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'stashed')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: '.'.join([project_short_name,'in']),
  output: meson.project_name(),
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

stashed_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'custom_widgets.py',
  'shake_listener.py',
  'utils.py',
]

install_data(stashed_sources, install_dir: moduledir)
