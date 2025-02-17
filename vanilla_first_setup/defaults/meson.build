pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
defaultsdir = join_paths(pkgdatadir, 'vanilla_first_setup/defaults')

sources = [
  '__init__.py',
  'applications.py',
  'conn_check.py',
  'hostname.py',
  'keyboard.py',
  'language.py',
  'locations.py',
  'theme.py',
  'timezone.py',
  'user.py',
  'welcome_user.py',
  'welcome.py',
]

install_data(sources, install_dir: defaultsdir)
