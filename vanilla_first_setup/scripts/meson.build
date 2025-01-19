pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
scriptsdir = join_paths(pkgdatadir, 'vanilla_first_setup/scripts')

sources = [
  'flatpak',
  'hostname',
  'keyboard',
  'live-keyboard',
  'locale',
  'logout',
  'theme',
  'timezone',
  'user',
]

install_data(sources, install_dir: scriptsdir)
